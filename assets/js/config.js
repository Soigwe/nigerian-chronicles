/**
 * NAIJA CHRONICLES — Global Configuration
 * Set your public Supabase credentials here for seamless, zero-config live updates.
 */

window.CHRONICLE_CONFIG = {
  // Replace these with your live Supabase project credentials
  supabaseUrl: localStorage.getItem('chronicle_supabase_url') || '',
  supabaseAnonKey: localStorage.getItem('chronicle_supabase_key') || '',
  
  // Editorial Metadata
  siteName: 'Naija Chronicles',
  tagline: 'Truth Through Scrutiny • Design Through Purpose',
  version: '2.4.0'
};
