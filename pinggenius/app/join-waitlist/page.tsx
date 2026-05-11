'use client'

import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog'
import { AlertDialogFooter, AlertDialogHeader } from '@/components/ui/alert-dialog'
import Link from 'next/link'

export default function WaitlistPage() {
    const [email, setEmail] = useState('')
    const [linkedin, setLinkedin] = useState('')
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState('')
    const [openModal, setOpenModal] = useState(false)

    const validateEmail = (email: string) => {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return regex.test(email)
    }

    const handleJoinWaitlist = async () => {
        setLoading(true)
        setError('')
        setSuccess(false)

        if (!email) {
            setError('Email is required')
            setLoading(false)
            return
        }

        if (!validateEmail(email)) {
            setError('Please enter a valid email')
            setLoading(false)
            return
        }

        try {
            const res = await fetch('/api/save-waitlist-user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, linkedin }),
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err?.message || 'Something went wrong')
            }

            setSuccess(true)
            setOpenModal(true)
            setEmail('')
            setLinkedin('')
        } catch (err: any) {
            setError(err.message || 'Something went wrong')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-black flex items-center justify-center px-4">
            <div className="absolute top-10 left-10 w-60 h-60 rounded-full bg-blue-600/10 blur-3xl animate-pulse-slow" />

            <div className="max-w-lg w-full bg-neutral-900 border border-blue-800 shadow-lg rounded-2xl p-8 space-y-6 text-center">
                <h1 className="text-3xl font-bold text-white">
                    Join the <span className="text-blue-500">PingGenius Beta</span>
                </h1>
                <p className="text-neutral-400 text-base">
                    Be among the first to send LinkedIn DMs that people actually reply to.
                </p>
                <p className="text-sm text-neutral-500">
                    Limited beta spots • Early users get lifetime discounted pricing
                </p>

                {/* Input fields */}
                <div className="flex flex-col sm:flex-row items-center gap-3 mt-4">
                    <Input
                        type="email"
                        placeholder="you@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="flex-1 border border-blue-700 focus:ring-blue-500 focus:border-blue-500 bg-neutral-800 text-white placeholder:text-neutral-500"
                    />
                    <Input
                        type="text"
                        placeholder="LinkedIn URL (optional)"
                        value={linkedin}
                        onChange={(e) => setLinkedin(e.target.value)}
                        className="flex-1 border border-blue-700 focus:ring-blue-500 focus:border-blue-500 bg-neutral-800 text-white placeholder:text-neutral-500"
                    />
                    <Button
                        onClick={handleJoinWaitlist}
                        disabled={loading || !email}
                        className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg w-full sm:w-auto transition-all hover:scale-105 hover:shadow-lg"
                    >
                        {loading ? 'Joining...' : 'Join Beta'}
                    </Button>
                </div>

                {/* Feedback */}
                {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
                {success && (
                    <p className="text-green-500 text-base mt-2">
                        ✅ You’ve been added to the waitlist!.
                    </p>
                )}

                {/* Trust badges */}
                <div className="flex flex-wrap justify-center gap-4 mt-6 text-sm text-neutral-400">
                    <div className="flex items-center gap-1">✅ No spam</div>
                    <div className="flex items-center gap-1">🔒 Privacy respected</div>
                    <div className="flex items-center gap-1">⚡ Early access</div>
                </div>
            </div>

            {/* ShadCN Modal for success */}
            <Dialog open={openModal} onOpenChange={setOpenModal}>
                <DialogContent className="bg-neutral-900 border border-blue-700 rounded-2xl p-6">
                    <AlertDialogHeader>
                        <DialogTitle className="text-2xl text-white font-bold mb-2">
                            🎉 You're on the Beta Waitlist!
                        </DialogTitle>
                        <DialogDescription className="text-neutral-400 text-base">
                            Thanks for signing up! Your spot is reserved. Stay tuned for early access updates.
                        </DialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Button
                            variant="outline"
                            className="cursor-pointer text-blue-400 border-blue-500 hover:bg-blue-950"
                            onClick={() => setOpenModal(false)}
                        >
                            Close
                        </Button>

                        <Link
                            href="https://x.com/HasnainXdev"
                            target="_blank"
                            className="text-sm text-blue-500 hover:underline text-center"
                        >
                            Follow me on X @HasnainXdev
                        </Link>
                    </AlertDialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
