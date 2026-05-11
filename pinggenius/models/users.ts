import mongoose from "mongoose"


const UsageSchema = new mongoose.Schema({
    emailAnalyses: { type: Number, required: true, default: 0 },
    autoReplies: { type: Number, required: true, default: 0 },
    sequencesCreated: { type: Number, required: true, default: 0 },
    contactsImported: { type: Number, required: true, default: 0 },
    lastReset: { type: Date, default: Date.now },
});

const UsersSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    role: { type: String, required: true, enum: ['user', 'admin'], default: 'user' },
    isWaitlisted: { type: Boolean, required: true, default: false },
    // refresh_token: { type: String, required: true, unique: true },
    isProUser: { type: Boolean, required: true, default: false },
    lemonCustomerId: { type: String, default: null },
    usage: { type: UsageSchema, required: true, default: {} },

}, { timestamps: true }
)

const Users = mongoose.models.Users || mongoose.model('Users', UsersSchema)

export default Users