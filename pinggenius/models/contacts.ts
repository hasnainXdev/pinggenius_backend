import mongoose from "mongoose";

const contactSchema = new mongoose.Schema({
    user_id: { type: String, required: true },
    name: { type: String, required: true, unique: true },
    linkedin_url: { type: String, required: true },
    email: { type: String, required: true },
    website: { type: String, required: true },
    tone: { type: String, required: true },
    selected_email: { type: String, required: true },
    status: { type: String, required: true },
}, { timestamps: true });


const Contacts = mongoose.models.Contacts || mongoose.model("contacts", contactSchema);

export default Contacts;