import React from 'react';

const SocialProof = () => {
  return (
    <section className="py-16 bg-black">
      <div className="max-w-6xl mx-auto px-4">
        <div className="text-center mb-12">
          <h3 className="text-2xl font-semibold text-white mb-8">Trusted by professionals who value results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-neutral-900/50 p-6 rounded-xl border border-white/10">
              <div className="text-yellow-400 text-2xl mb-2">★★★★★</div>
              <p className="text-neutral-300 mb-4">
                "Finally, a tool that understands the difference between automation and personalization. 
                My reply rates increased by 3x since switching to PingGenius."
              </p>
              <div className="text-white font-medium">Sarah K., Growth Lead</div>
              <div className="text-neutral-500 text-sm">SaaS Startup</div>
            </div>
            
            <div className="bg-neutral-900/50 p-6 rounded-xl border border-white/10">
              <div className="text-yellow-400 text-2xl mb-2">★★★★★</div>
              <p className="text-neutral-300 mb-4">
                "The tone customization is brilliant. I can match my outreach to my personal style 
                while still saving hours on message creation."
              </p>
              <div className="text-white font-medium">Michael T., Founder</div>
              <div className="text-neutral-500 text-sm">B2B Consulting</div>
            </div>
            
            <div className="bg-neutral-900/50 p-6 rounded-xl border border-white/10">
              <div className="text-yellow-400 text-2xl mb-2">★★★★★</div>
              <p className="text-neutral-300 mb-4">
                "Account safety was my biggest concern. PingGenius delivers personalized outreach 
                without risking my LinkedIn account."
              </p>
              <div className="text-white font-medium">James L., Sales Director</div>
              <div className="text-neutral-500 text-sm">Enterprise Tech</div>
            </div>
          </div>
        </div>
        
        <div className="text-center pt-8 border-t border-white/10">
          <div className="inline-flex items-center gap-8 text-sm text-neutral-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Used by 500+ professionals</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>3x higher reply rates</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Zero account issues</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProof;