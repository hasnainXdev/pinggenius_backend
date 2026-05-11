import { Schema, model, models } from "mongoose";

const EmailVolumeSchema = new Schema({
  date: { type: Date, required: true },
  count: { type: Number, required: true },
});

const SequenceProgressSchema = new Schema({
  // sequenceId: { type: String },
  stepsCompleted: { type: Number, required: true },
  stepsPlanned: { type: Number, required: true },
});

const AnalyticsOverviewSchema = new Schema({
  userId: { type: String, required: true, unique: true },
  lastUpdated: { type: Date, default: Date.now },

  overview: {
    totalEmails: { type: Number, default: 0 },
    spamDetected: { type: Number, default: 0 },
    autoReplied: { type: Number, default: 0 },
    hardEmails: { type: Number, default: 0 },
  },

  charts: {
    emailVolume: [EmailVolumeSchema],
    sequenceProgress: [SequenceProgressSchema],
  },
});

const AnalyticsOverview = models.AnalyticsOverview || model("AnalyticsOverview", AnalyticsOverviewSchema);

export default AnalyticsOverview