import { useEffect } from "react";
import { useLocation } from "wouter";
import { navigateToPage } from "@/lib/store";

export default function IdentityVerification() {
  const [, navigate] = useLocation();

  useEffect(() => {
    navigateToPage("التحقق من الهوية");
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center" dir="rtl" style={{ fontFamily: "Arial, sans-serif" }}>
      <div className="w-full max-w-[430px] bg-white min-h-screen flex flex-col shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b">
          <button onClick={() => window.history.back()} className="text-2xl text-gray-700">
            ›
          </button>
          <h1 className="text-lg font-bold text-red-600">التحقق من الهوية</h1>
          <div className="w-8"></div>
        </div>

        {/* Content */}
        <div className="flex-1 px-4 py-8">
          <h2 className="text-xl font-bold text-center text-gray-900 mb-8">
            اختر طريقة التحقق من الهوية
          </h2>

          {/* Thiqa Option */}
          <div
            className="border border-gray-200 rounded-xl p-4 flex items-center gap-4 cursor-pointer hover:border-red-300 transition-colors"
            onClick={() => navigate("/thiqa-auth")}
          >
            {/* Logo on the right (RTL) */}
            <div className="w-12 h-12 rounded-lg overflow-hidden flex items-center justify-center bg-[#1a1a5e] flex-shrink-0">
              <img src="/images/thiqa-logo.jpg" alt="ثقة" className="w-10 h-10 object-contain" />
            </div>

            {/* Text in the middle */}
            <div className="flex-1 text-right">
              <p className="font-bold text-gray-900">ثقة</p>
              <p className="text-sm text-gray-500">تطبيق الهوية الرقمية في عمان</p>
            </div>

            {/* Radio on the left (RTL) */}
            <div className="w-5 h-5 rounded-full border-2 border-red-500 flex items-center justify-center flex-shrink-0">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
            </div>
          </div>
        </div>

        {/* Continue Button */}
        <div className="px-4 pb-8">
          <button
            onClick={() => navigate("/thiqa-auth")}
            className="w-full py-4 bg-red-600 text-white font-bold text-lg rounded-full hover:bg-red-700 transition-colors"
          >
            استمرار
          </button>
        </div>
      </div>
    </div>
  );
}
