"use client"
import React from 'react'
import { usePathname } from 'next/navigation'
import Footer from './Footer'
const FooterProvider = () => {

    const pathname = usePathname()

    const isProtectedRoute = pathname.startsWith("/waitlist") ||
        pathname.startsWith("/sign-in") ||
        pathname.startsWith("/dashboard");


    return (
        <>
            {!isProtectedRoute && <Footer />}
        </>
    )
}

export default FooterProvider
