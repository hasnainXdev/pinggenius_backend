import { CheckCircle } from "lucide-react";
import { ReactNode } from "react";

interface FeatureCardProps {
    icon: ReactNode;
    title: string;
    description: string;
    points: string[];
}

export default function FeatureCard({
    icon,
    title,
    description,
    points,
}: FeatureCardProps) {
    return (
        <div className="
      group relative rounded-2xl p-8 bg-black/60 border border-white/10 backdrop-blur transition-all duration-300 hover:border-blue-500/40 hover:-translate-y-1">
            {/* Icon */}
            <div className="
        mb-6 flex h-12 w-12 items-center justify-center
        rounded-xl
        bg-gradient-to-br from-blue-500 to-blue-700
        group-hover:scale-110 transition-transform duration-200
      ">
                {icon}
            </div>

            {/* Title */}
            <h3 className="text-xl font-semibold text-white mb-3">
                {title}
            </h3>

            {/* Description */}
            <p className="text-sm text-white/70 leading-relaxed mb-6">
                {description}
            </p>

            {/* Points */}
            <ul className="space-y-3">
                {points.map((point, index) => (
                    <li
                        key={index}
                        className="flex items-start gap-2 text-sm text-white/60"
                    >
                        <CheckCircle className="w-4 h-4 text-blue-500 mt-[2px] flex-shrink-0" />
                        <span>{point}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
