import mongoose from "mongoose";

const emailSchema = new mongoose.Schema({
    user_id: { type: String, required: true },
    subject: { type: String, required: true },
    to_email: { type: String, required: true },
    reply: { type: String },
    status: { type: String, enum: ["junk", "easy", "hard"], required: true },
}, { timestamps: true });

const Email = mongoose.models.Email || mongoose.model("emails", emailSchema);

export default Email;