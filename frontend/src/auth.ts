import NextAuth from 'next-auth';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { prisma } from '@/lib/prisma';
import CredentialsProvider from 'next-auth/providers/credentials';

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: 'database',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  providers: [
    CredentialsProvider({
      name: 'Phone OTP',
      credentials: {
        phone: { label: 'Phone Number', type: 'text' },
        otp: { label: 'OTP', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.phone || !credentials?.otp) return null;

        // In production, verify OTP against Redis / Exotel verification API.
        // For Phase 0 / local dev test verification:
        if (credentials.otp === '1234') {
          let user = await prisma.user.findUnique({
            where: { phone: credentials.phone },
          });

          if (!user) {
            user = await prisma.user.create({
              data: {
                phone: credentials.phone,
                name: `User ${credentials.phone.slice(-4)}`,
                role: 'SHIPPER_PERSONAL',
                isVerified: true,
              },
            });
          }

          return user;
        }

        return null;
      },
    }),
  ],
  callbacks: {
    async session({ session, user }) {
      if (session.user && user) {
        session.user.id = user.id;
        // @ts-expect-error custom user fields
        session.user.phone = user.phone;
        // @ts-expect-error custom user fields
        session.user.role = user.role;
        // @ts-expect-error custom user fields
        session.user.isVerified = user.isVerified;
      }
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
});
