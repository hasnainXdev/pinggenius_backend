import { getServerSession } from "next-auth";
import { authOptions } from "./auth";

export const auth = async () => await getServerSession(authOptions);