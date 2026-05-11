"use client";

import { User, Settings, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { signOut, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface TopBarProps {
    title: string;
}

export function TopBar({ title }: TopBarProps) {

    const { data: session } = useSession();
    const router = useRouter()

    const handleLogout = () => {
        signOut();
        router.push("/");
    };

    return (
        <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-16 items-center justify-between px-10">
                {/* Left Section */}
                <div className="flex items-center space-x-4">
                    <h1 className="hidden md:block text-xl font-semibold text-foreground">{title}</h1>

                </div>

                {/* Right Section */}
                <div className="flex items-center space-x-3">

                    {/* User Menu */}
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="relative h-8 w-8 rounded-full cursor-pointer">
                                <Avatar className="h-8 w-8">
                                    <AvatarFallback className="bg-primary text-primary-foreground">
                                        <User className="w-4 h-4" />
                                    </AvatarFallback>
                                </Avatar>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56 bg-popover" align="end" forceMount>
                            <DropdownMenuLabel className="font-normal">
                                {
                                    session?.user ? (

                                        <div className="flex flex-col space-y-1">
                                            <p className="text-sm font-medium leading-none">{session?.user?.name}</p>
                                            <p className="text-xs leading-none text-muted-foreground">
                                                {session?.user?.email}
                                            </p>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col space-y-1">
                                            <p className="text-sm font-medium leading-none">Jhon Doe</p>
                                            <p className="text-xs leading-none text-muted-foreground">
                                                6d6kO@example.com
                                            </p>
                                        </div>
                                    )
                                }
                            </DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            {/* <DropdownMenuItem className="cursor-pointer">
                                <User className="mr-2 h-4 w-4 hover:text-white" />
                                <span>Profile</span>
                            </DropdownMenuItem> */}
                            {/* TODO: Add settings page 🎯*/}

                                <Link href={"/dashboard/settings"}>
                            <DropdownMenuItem className="cursor-pointer">
                                    <Settings className="mr-2 h-4 w-4 hover:text-white" />
                                    <span>Settings</span>
                            </DropdownMenuItem>
                                </Link>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-destructive cursor-pointer">
                                <LogOut className="mr-2 h-4 w-4 hover:text-red-600" />
                                <span onClick={() => handleLogout()}>Sign out</span>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
        </header>
    );
}