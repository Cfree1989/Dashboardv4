import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to dashboard as specified in masterplan
  redirect('/dashboard');
}
