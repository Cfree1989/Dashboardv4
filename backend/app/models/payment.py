# Payment Model - 3D Print Management System
"""
Payment model for tracking financial transactions when students pick up completed prints.
Records actual weight, final cost, and Tiger-Cash transaction details.
"""

from datetime import datetime
from app.database import db


class Payment(db.Model):
    """
    Payment model for completed print transactions.
    
    Records final payment details when students collect their completed prints,
    including actual weight from scale and Tiger-Cash transaction information.
    """
    
    __tablename__ = 'payment'
    
    # Primary key is job_id (one payment per job)
    job_id = db.Column(db.String(36), db.ForeignKey('job.id'), primary_key=True)
    
    # Payment details
    grams = db.Column(db.Float, nullable=False)           # Actual weight from scale
    price_cents = db.Column(db.Integer, nullable=False)   # Final price in cents
    txn_no = db.Column(db.String(50), nullable=False)     # Tiger-Cash transaction number
    
    # Pickup details
    picked_up_by = db.Column(db.String(100), nullable=False)  # Person who collected print
    paid_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_by_staff = db.Column(db.String(100), nullable=False) # Staff member who processed payment
    
    # Optional fields
    notes = db.Column(db.Text, nullable=True)  # Payment or pickup notes
    
    def __repr__(self):
        return f'<Payment {self.job_id}: ${self.price_usd:.2f} (TXN: {self.txn_no})>'
    
    @property
    def price_usd(self):
        """Convert price from cents to USD."""
        return self.price_cents / 100.0
    
    @price_usd.setter
    def price_usd(self, value):
        """Set price in USD (converts to cents)."""
        self.price_cents = int(round(value * 100))
    
    @property
    def days_since_payment(self):
        """Calculate days since payment was processed."""
        return (datetime.utcnow() - self.paid_ts).days
    
    def calculate_cost_difference(self):
        """
        Calculate difference between estimated and actual cost.
        
        Returns:
            dict: Contains estimated_cost, actual_cost, difference, and percentage_change
        """
        if not self.job:
            return None
        
        estimated_cost = float(self.job.cost_usd) if self.job.cost_usd else 0
        actual_cost = self.price_usd
        difference = actual_cost - estimated_cost
        
        percentage_change = 0
        if estimated_cost > 0:
            percentage_change = (difference / estimated_cost) * 100
        
        return {
            'estimated_cost': estimated_cost,
            'actual_cost': actual_cost,
            'difference': difference,
            'percentage_change': round(percentage_change, 2)
        }
    
    def to_dict(self):
        """Convert payment to dictionary for API responses."""
        cost_analysis = self.calculate_cost_difference()
        
        return {
            'job_id': self.job_id,
            'grams': self.grams,
            'price_usd': self.price_usd,
            'price_cents': self.price_cents,
            'txn_no': self.txn_no,
            'picked_up_by': self.picked_up_by,
            'paid_ts': self.paid_ts.isoformat(),
            'paid_by_staff': self.paid_by_staff,
            'notes': self.notes,
            'days_since_payment': self.days_since_payment,
            'cost_analysis': cost_analysis
        }
    
    @classmethod
    def create_payment(cls, job_id, grams, price_usd, txn_no, picked_up_by, paid_by_staff, notes=None):
        """
        Create payment record for completed job.
        
        Args:
            job_id (str): Job ID
            grams (float): Actual weight from scale
            price_usd (float): Final price in USD
            txn_no (str): Tiger-Cash transaction number
            picked_up_by (str): Person who collected the print
            paid_by_staff (str): Staff member who processed payment
            notes (str, optional): Additional notes
            
        Returns:
            Payment: Created payment instance
        """
        payment = cls(
            job_id=job_id,
            grams=grams,
            txn_no=txn_no,
            picked_up_by=picked_up_by,
            paid_by_staff=paid_by_staff,
            notes=notes
        )
        payment.price_usd = price_usd  # Uses setter to convert to cents
        
        db.session.add(payment)
        return payment
    
    @classmethod
    def get_payments_by_date_range(cls, start_date, end_date):
        """Get payments within a date range."""
        return cls.query.filter(
            cls.paid_ts >= start_date,
            cls.paid_ts <= end_date
        ).order_by(cls.paid_ts.desc()).all()
    
    @classmethod
    def get_revenue_summary(cls, start_date=None, end_date=None):
        """
        Get revenue summary for a date range.
        
        Returns:
            dict: Summary with total_revenue, total_jobs, average_price, etc.
        """
        query = cls.query
        if start_date:
            query = query.filter(cls.paid_ts >= start_date)
        if end_date:
            query = query.filter(cls.paid_ts <= end_date)
        
        payments = query.all()
        
        if not payments:
            return {
                'total_revenue': 0.0,
                'total_jobs': 0,
                'average_price': 0.0,
                'total_grams': 0.0,
                'minimum_charges': 0
            }
        
        total_revenue = sum(p.price_usd for p in payments)
        total_jobs = len(payments)
        total_grams = sum(p.grams for p in payments)
        minimum_charges = sum(1 for p in payments if p.price_cents == 300)  # $3.00 minimum
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_jobs': total_jobs,
            'average_price': round(total_revenue / total_jobs, 2),
            'total_grams': round(total_grams, 2),
            'minimum_charges': minimum_charges,
            'minimum_charge_percentage': round((minimum_charges / total_jobs) * 100, 2)
        }
    
    @classmethod
    def get_payments_by_staff(cls, staff_name, limit=50):
        """Get recent payments processed by specific staff member."""
        return cls.query.filter_by(paid_by_staff=staff_name)\
                       .order_by(cls.paid_ts.desc())\
                       .limit(limit).all()