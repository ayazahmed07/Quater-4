import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/lib/query";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Lubricant Inventory Management",
  description: "Complete inventory management system for fuel pump lubricants",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
