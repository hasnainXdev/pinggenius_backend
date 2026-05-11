import mongoose from "mongoose";

const HardEmailSchema = new mongoose.Schema({
    subject: { type: String, required: true, },
    sender: { type: String, required: true },
    snippet: { type: String, required: true },
    id: { type: String, required: true },
    type: { type: String, required: true },
    source: { type: String, required: true },
    status: { type: String, required: true },
}, { timestamps: true });

const HardEmails = mongoose.models.HardEmails || mongoose.model('hard_emails', HardEmailSchema);

export default HardEmails;