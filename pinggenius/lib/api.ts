import axios from 'axios';
import type { Sequence, OutreachContext } from './demo-data';

// Define the base URL for the backend API
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_FAST_API_URL || 'http://localhost:8000';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Type definitions for API responses
interface ProfileAnalysisRequest {
  user_id: string;  // ID of the user performing the analysis
  url: string;
  role: string;
  company?: string;
  industry?: string;
  recent_activity?: string;
  tone: string;
}

interface ProfileAnalysisResponse {
  success: boolean;
  data: {
    id: string;
    url: string;
    role: string;
    company?: string;
    industry?: string;
    recent_activity?: string;
  };
  message?: string;
  actionable_alternative?: string;
}

interface GenerateRequest {
  user_id: string;  // ID of the user generating the sequence
  profile_id: string;
  tone: string;
}

interface GenerateResponse {
  success: boolean;
  data: {
    id: string;
    profile_id: string;
    connection_note: string;
    dm_1: string;
    follow_up_1: string;
    follow_up_2: string;
    tone: string;
    predicted_reply_score: number;
    created_at: string;
    updated_at: string;
  };
  message?: string;
  actionable_alternative?: string;
}

/**
 * Analyzes a LinkedIn profile and stores it in the backend
 */
export async function analyzeProfile(ctx: OutreachContext, userId: string): Promise<{ profileId: string }> {
  if (!userId) {
    throw new Error("User ID is required for profile analysis");
  }
  try {
    // Map frontend tone values to backend tone values (capitalize first letter)
    const toneMap: Record<string, string> = {
      'friendly': 'Friendly',
      'direct': 'Direct',
      'authority': 'Authority',
      'casual': 'Casual',
    };

    const mappedTone = toneMap[ctx.tone] || 'Friendly'; // Default to Friendly if mapping not found

    const requestBody: ProfileAnalysisRequest = {
      user_id: userId,  // Pass the user ID to the backend
      url: ctx.url,
      role: ctx.role,
      company: ctx.company,
      industry: ctx.industry,
      recent_activity: ctx.recent_activity,
      tone: mappedTone,
    };

    const response = await apiClient.post<ProfileAnalysisResponse>('/api/v1/profile/analyze', requestBody);

    if (!response.data.success) {
      // Check if the response contains user-friendly error info
      const errorMessage = response?.data?.message || 'Profile analysis failed';
      const actionableTip = response?.data?.actionable_alternative || 'Please try again or contact support if the issue persists';
      
      throw new Error(`${errorMessage} - ${actionableTip}`);
    }

    return { profileId: response.data.data.id };
  } catch (error) {
    console.error('Error analyzing profile:', error);

    // Check if it's a network error (no internet, timeout, etc.)
    if (axios.isAxiosError(error)) {
      // Network error handling
      if (!error.response) {
        // No response means network error (offline, timeout, etc.)
        throw new Error("It looks like you're offline or experiencing network issues! 🌐 Please check your internet connection and try again.");
      }

      // Check if the error response contains user-friendly error info
      const errorResponse = error.response?.data;
      if (errorResponse?.message && errorResponse?.actionable_alternative) {
        throw new Error(`${errorResponse.message} - ${errorResponse.actionable_alternative}`);
      }
      throw new Error(errorResponse?.message || error.message || 'Network error occurred');
    }

    // For other types of errors
    throw error;
  }
}

// Type for sequence without the 'copied' and 'sent' flags but with the ID
type SequenceWithId = Omit<Sequence, 'copied' | 'sent'>;

/**
 * Generates an outreach sequence based on a profile
 */
export async function generateOutreachSequence(userId: string, profileId: string, tone: string, ctx?: OutreachContext): Promise<SequenceWithId> {
  if (!userId) {
    throw new Error("User ID is required for sequence generation");
  }
  try {
    // Map frontend tone values to backend tone values (capitalize first letter)
    const toneMap: Record<string, string> = {
      'friendly': 'Friendly',
      'direct': 'Direct',
      'authority': 'Authority',
      'casual': 'Casual',
    };

    const mappedTone = toneMap[tone] || 'Friendly'; // Default to Friendly if mapping not found

    const requestBody: GenerateRequest = {
      user_id: userId,  // Pass the user ID to the backend
      profile_id: profileId,
      tone: mappedTone,
    };

    const response = await apiClient.post<GenerateResponse>('/api/v1/outreach/generate', requestBody);

    if (!response.data.success) {
      const errorMessage = response.data.message || response?.data?.message || 'Sequence generation failed';
      const actionableTip = response?.data?.actionable_alternative || 'Please try again or contact support if the issue persists';
      throw new Error(`${errorMessage} - ${actionableTip}`);
    }

    // Map the backend response to the frontend Sequence type
    const backendData = response.data.data;

    // Use the predicted reply score from the backend if available, otherwise calculate it
    const score = backendData.predicted_reply_score || (() => {
      // Calculate a predicted reply score based on the context (similar to mock-generator)
      let completeness = 1; // role is always present
      if (ctx?.company) completeness += 1;
      if (ctx?.industry) completeness += 1;
      if (ctx?.recent_activity) completeness += 1;

      const toneBoost: Record<string, number> = {
        friendly: 0.06,
        direct: 0.01,
        authority: 0.03,  // Added boost for authority tone
        casual: 0.05,     // Added boost for casual tone
      };

      const base = 0.60 + (completeness / 4) * 0.22 + (toneBoost[tone] || 0);
      const urlLen = ctx?.url.replace(/[^a-zA-Z]/g, "").length || 10;
      const jitter = ((urlLen % 17) / 17) * 0.08 - 0.04; // ±4%
      return Math.max(0.55, Math.min(0.95, Math.round((base + jitter) * 100) / 100));
    })();

    // Create the sequence object that matches the frontend type
    // Map backend messages to frontend message roles
    const sequence: SequenceWithId = {
      id: backendData.id, // Use the ID from the backend
      profile: ctx?.url || backendData.profile_id,
      tone: tone as any, // Use the lowercase tone directly
      generatedAt: backendData.created_at || new Date().toISOString(),
      predicted_reply_score: score,
      time_ms: 0, // We won't track this since the API call handles generation time
      context: ctx,
      messages: [
        { role: "connection", text: backendData.connection_note }, // Connection note
        { role: "cold", text: backendData.dm_1 }, // First DM as cold message
        { role: "followup1", text: backendData.follow_up_1 }, // First follow-up
        { role: "followup2", text: backendData.follow_up_2 }, // Second follow-up
      ],
    };

    return sequence;
  } catch (error) {
    console.error('Error generating outreach sequence:', error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || error.message || 'Network error occurred');
    }
    throw error;
  }
}

/**
 * Generates a complete outreach sequence by first analyzing the profile and then generating the sequence
 */
export async function generateCompleteSequence(ctx: OutreachContext, userId: string): Promise<Sequence> {
  if (!userId) {
    throw new Error("User ID is required for sequence generation");
  }
  // First analyze the profile
  const { profileId } = await analyzeProfile(ctx, userId);

  // Then generate the sequence
  const sequence = await generateOutreachSequence(userId, profileId, ctx.tone, ctx);

  // Create a complete sequence object with all required properties
  return {
    ...sequence,
    id: sequence.id, // Use backend ID if available, otherwise generate one
    copied: false,
    sent: false,
  };
}

/**
 * Fetches an outreach sequence by its ID from the backend
 */
export async function getSequenceById(sequenceId: string, userId?: string): Promise<Sequence> {
  try {
    // Construct the URL with user ID as query parameter if provided
    let url = `/api/v1/outreach/${sequenceId}`;
    if (userId) {
      url += `?user_id=${encodeURIComponent(userId)}`;
    }

    const response = await apiClient.get(url);

    if (!response.data.success) {
      throw new Error(response.data.message || response.data.data?.message || 'Failed to fetch sequence');
    }

    const backendData = response.data.data;

    // Use the predicted reply score from the backend if available, otherwise calculate it
    const score = backendData.predicted_reply_score || (() => {
      // Calculate a predicted reply score based on the context (similar to mock-generator)
      let completeness = 1; // role is always present
      if (backendData.company) completeness += 1;
      if (backendData.industry) completeness += 1;
      if (backendData.recent_activity) completeness += 1;

      const toneBoost: Record<string, number> = {
        friendly: 0.06,
        direct: 0.01,
        authority: 0.03,  // Added boost for authority tone
        casual: 0.05,     // Added boost for casual tone
      };

      // Since we don't have the original context, we'll use a default calculation
      const base = 0.60 + (completeness / 4) * 0.22 + (toneBoost[backendData.tone.toLowerCase()] || 0);
      const urlLen = backendData.url?.replace(/[^a-zA-Z]/g, "").length || 10;
      const jitter = ((urlLen % 17) / 17) * 0.08 - 0.04; // ±4%
      return Math.max(0.55, Math.min(0.95, Math.round((base + jitter) * 100) / 100));
    })();

    // Create the sequence object that matches the frontend type
    const sequence: Sequence = {
      id: backendData.id,
      profile: backendData.url || backendData.profile_id,
      tone: backendData.tone.toLowerCase() as any, // Use the lowercase tone directly
      generatedAt: backendData.created_at || new Date().toISOString(),
      predicted_reply_score: score,
      time_ms: 0, // We won't track this since this is a fetch operation
      context: {
        url: backendData.url || backendData.profile_id,
        role: backendData.role || '',
        company: backendData.company,
        industry: backendData.industry,
        recent_activity: backendData.recent_activity,
        tone: backendData.tone.toLowerCase() as any,
      },
      messages: [
        { role: "connection", text: backendData.connection_note }, // Connection note
        { role: "cold", text: backendData.dm_1 }, // First DM as cold message
        { role: "followup1", text: backendData.follow_up_1 }, // First follow-up
        { role: "followup2", text: backendData.follow_up_2 }, // Second follow-up
      ],
      copied: false,
      sent: false,
    };

    return sequence;
  } catch (error) {
    console.error('Error fetching sequence by ID:', error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || error.message || 'Network error occurred');
    }
    throw error;
  }
}

/**
 * Fetches all sequences for a user from the backend
 */
export async function getAllSequences(userId?: string): Promise<Sequence[]> {
  try {
    // If no user ID is provided, return an empty array
    if (!userId) {
      return [];
    }

    // Pass the user ID as a query parameter
    const response = await apiClient.get(`/api/v1/outreach/?user_id=${userId}`);

    if (!response.data.success) {
      throw new Error(response.data.message || response.data.data?.message || 'Failed to fetch sequences');
    }

    const backendData = response.data.data;

    // Transform the backend data to the frontend Sequence type
    const sequences: Sequence[] = (backendData.sequences || []).map((backendSeq: any) => {
      // Use the predicted reply score from the backend if available, otherwise calculate it
      const score = backendSeq.predicted_reply_score || (() => {
        // Calculate a predicted reply score based on the context
        let completeness = 1; // role is always present
        if (backendSeq.context?.company) completeness += 1;
        if (backendSeq.context?.industry) completeness += 1;
        if (backendSeq.context?.recent_activity) completeness += 1;

        const toneBoost: Record<string, number> = {
          friendly: 0.06,
          direct: 0.01,
          authority: 0.03,  // Added boost for authority tone
          casual: 0.05,     // Added boost for casual tone
        };

        // Since we don't have the original context, we'll use a default calculation
        const base = 0.60 + (completeness / 4) * 0.22 + (toneBoost[backendSeq.tone.toLowerCase()] || 0);
        const urlLen = backendSeq.url?.replace(/[^a-zA-Z]/g, "").length || 10;
        const jitter = ((urlLen % 17) / 17) * 0.08 - 0.04; // ±4%
        return Math.max(0.55, Math.min(0.95, Math.round((base + jitter) * 100) / 100));
      })();

      return {
        id: backendSeq.id,
        profile: backendSeq.url || backendSeq.profile_id,
        tone: backendSeq.tone.toLowerCase() as any, // Use the lowercase tone directly
        generatedAt: backendSeq.created_at || new Date().toISOString(),
        predicted_reply_score: score,
        time_ms: 0, // We won't track this since this is a fetch operation
        context: {
          url: backendSeq.url || backendSeq.profile_id,
          role: backendSeq.role || '', // This might not be available in the sequence data
          company: backendSeq.company,
          industry: backendSeq.industry,
          recent_activity: backendSeq.recent_activity,
          tone: backendSeq.tone.toLowerCase() as any,
        },
        messages: [
          { role: "connection", text: backendSeq.connection_note }, // Connection note
          { role: "cold", text: backendSeq.dm_1 }, // First DM as cold message
          { role: "followup1", text: backendSeq.follow_up_1 }, // First follow-up
          { role: "followup2", text: backendSeq.follow_up_2 }, // Second follow-up
        ],
        copied: false,
        sent: false,
      };
    });

    return sequences;
  } catch (error) {
    console.error('Error fetching all sequences:', error);
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || error.message || 'Network error occurred');
    }
    throw error;
  }
}

