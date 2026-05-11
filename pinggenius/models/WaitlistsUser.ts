import mongoose from "mongoose"

const WaitlistsUserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    role: { type: String, required: true, enum: ['user', 'admin'], default: 'user' },
    isWaitlisted: { type: Boolean, required: true, default: false },

}, { timestamps: true }
)

const WaitlistsUser = mongoose.models.WaitlistsUser || mongoose.model('WaitlistsUser', WaitlistsUserSchema)

export default WaitlistsUser