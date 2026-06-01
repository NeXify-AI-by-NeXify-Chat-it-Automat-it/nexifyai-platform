// Stub for Supabase client. Replace with actual Supabase project URL and anon key.
export const supabase = {
  auth: {
    signUp: async ({ email, password }: { email: string; password: string }) => {
      console.log('signUp', email, password);
      return { data: { user: { email } }, error: null };
    },
    signInWithPassword: async ({ email, password }: { email: string; password: string }) => {
      console.log('signIn', email, password);
      return { data: { user: { email } }, error: null };
    },
    signOut: async () => {
      return { error: null };
    },
  },
};
