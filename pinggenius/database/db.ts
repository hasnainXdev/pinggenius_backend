import mongoose from "mongoose";

/**
 * MongoDB connection handler with singleton pattern and connection state management
 */

const MONGODB_URI = process.env.MONGODB_URI;

if (!MONGODB_URI) {
    throw new Error(
        "MongoDB connection error: Please define the MONGODB_URI environment variable"
    );
}

// Maintain cached mongoose instance to prevent duplicate connections
let cachedMongoose: typeof mongoose | null = null;

const connectDB = async (): Promise<void> => {
    try {
        // Return immediately if existing healthy connection is present
        if (mongoose.connection.readyState === 1) {
            console.log("✅ Using existing MongoDB connection");
            return;
        }

        // Prevent duplicate connections during connection attempt
        if (mongoose.connection.readyState === 2) {
            console.log("⚠️ MongoDB connection already in progress");
            return;
        }

        // Use cached instance if available
        if (cachedMongoose) {
            console.log("♻️ Reusing existing MongoDB connection");
            return;
        }

        // Establish new connection with proper type handling
        console.log("⏳ Establishing new MongoDB connection...");
        cachedMongoose = await mongoose.connect(MONGODB_URI);
        const connection = cachedMongoose.connection;

        console.log(`✅ MongoDB connected successfully (Host: ${connection.host})`);

        // Set up connection cleanup on process termination
        process.on("SIGINT", async () => {
            await connection.close();
            console.log("⚠️ MongoDB connection closed due to application termination");
            process.exit(0);
        });

    } catch (error) {
        console.error("❌ MongoDB connection failed:", error);
        cachedMongoose = null; // Reset cache on failure
        throw new Error(`Database connection error: ${error instanceof Error ? error.message : "Unknown error"}`);
    }
};

export default connectDB;