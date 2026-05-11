import mongoose from "mongoose";

const sequencesSchema = new mongoose.Schema({
    user_id: { type: String, required: true },
    contact_id: { type: String, required: true },
    email_body: { type: String, required: true },
    step: { type: Number, required: true },
    sent_at: { type: Date },
    next_sent_at: { type: Date },
    status: { type: String, required: true },

}, { timestamps: true });


const Sequences = mongoose.models.Sequence || mongoose.model("sequences", sequencesSchema);

export default Sequences