// Fiti API Tester & Firebase Auth Logic
document.addEventListener('DOMContentLoaded', () => {
  const getEl = (id) => document.getElementById(id);

  const baseUrlInput = getEl('baseUrl');
  const authTokenInput = getEl('authToken');
  const mockAuthInput = getEl('mockAuth');
  const mockUidRow = getEl('mockUidRow');
  const mockUidInput = getEl('mockUid');
  const contentArea = getEl('content');
  const responseBody = getEl('responseBody');
  const statusBadge = getEl('statusBadge');
  const timeBadge = getEl('timeBadge');
  const copyBtn = getEl('copyBtn');
  const toast = getEl('toast');

  // Firebase Config Elements
  const toggleFbConfigBtn = getEl('toggleFbConfigBtn');
  const fbConfigFields = getEl('fbConfigFields');
  const fbApiKeyInput = getEl('fbApiKey');
  const fbAuthDomainInput = getEl('fbAuthDomain');
  const fbProjectIdInput = getEl('fbProjectId');
  const saveFbConfigBtn = getEl('saveFbConfigBtn');

  // User status elements
  const userAvatar = getEl('userAvatar');
  const userName = getEl('userName');
  const userEmail = getEl('userEmail');
  const signOutBtn = getEl('signOutBtn');

  let currentUser = null;
  let currentIdToken = null;
  let db = null;

  // Load stored API Key if any
  const storedApiKey = localStorage.getItem('fiti_fb_api_key') || '';
  if (storedApiKey) fbApiKeyInput.value = storedApiKey;

  // Initialize Firebase
  function initFirebase() {
    const apiKey = fbApiKeyInput.value.trim() || 'AIzaSyBGbesTxWPOqshyBogCuUjS8pccJWitTdQ';
    const authDomain = fbAuthDomainInput.value.trim() || 'fiti-b0cb2.firebaseapp.com';
    const projectId = fbProjectIdInput.value.trim() || 'fiti-b0cb2';

    const firebaseConfig = {
      apiKey: apiKey,
      authDomain: authDomain,
      projectId: projectId,
      storageBucket: "fiti-b0cb2.firebasestorage.app",
      messagingSenderId: "1041965038766",
      appId: "1:1041965038766:web:7b6099b26931c41990c13f"
    };

    try {
      if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
      }
      db = firebase.firestore();

      // Listen for auth state
      firebase.auth().onAuthStateChanged(async (user) => {
        currentUser = user;
        if (user) {
          currentIdToken = await user.getIdToken();
          authTokenInput.value = currentIdToken;
          userName.textContent = user.displayName || user.email.split('@')[0];
          userEmail.textContent = user.email;
          if (user.photoURL) {
            userAvatar.style.backgroundImage = `url(${user.photoURL})`;
            userAvatar.textContent = '';
          } else {
            userAvatar.style.backgroundImage = 'none';
            userAvatar.textContent = (user.displayName || user.email || 'U')[0].toUpperCase();
          }
          signOutBtn.style.display = 'block';
          showToast(`Signed in as ${user.email}`);
        } else {
          currentIdToken = null;
          authTokenInput.value = '';
          userName.textContent = 'Not Signed In';
          userEmail.textContent = 'Sign in to sync token';
          userAvatar.style.backgroundImage = 'none';
          userAvatar.textContent = '?';
          signOutBtn.style.display = 'none';
        }
      });
    } catch (err) {
      console.warn('Firebase init status:', err.message);
    }
  }

  initFirebase();

  // Config toggle UI
  toggleFbConfigBtn.addEventListener('click', () => {
    fbConfigFields.style.display = fbConfigFields.style.display === 'none' ? 'block' : 'none';
  });

  saveFbConfigBtn.addEventListener('click', () => {
    if (fbApiKeyInput.value.trim()) {
      localStorage.setItem('fiti_fb_api_key', fbApiKeyInput.value.trim());
    }
    initFirebase();
    showToast('Firebase config updated!');
    fbConfigFields.style.display = 'none';
  });

  signOutBtn.addEventListener('click', () => {
    firebase.auth().signOut().then(() => showToast('Signed out successfully!'));
  });

  // Toggle Mock UID field
  mockAuthInput.addEventListener('change', () => {
    mockUidRow.style.display = mockAuthInput.checked ? 'block' : 'none';
  });

  // Navigation handlers
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
      renderSection(item.dataset.section);
    });
  });

  copyBtn.addEventListener('click', () => {
    const text = responseBody.innerText;
    if (text) {
      navigator.clipboard.writeText(text);
      showToast('Copied response to clipboard!');
    }
  });

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }

  function getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (mockAuthInput.checked && mockUidInput.value.trim()) {
      headers['Authorization'] = `Bearer ${mockUidInput.value.trim()}`;
    } else if (authTokenInput.value.trim()) {
      headers['Authorization'] = `Bearer ${authTokenInput.value.trim()}`;
    }
    return headers;
  }

  async function makeRequest(method, endpoint, body = null, queryParams = {}) {
    const baseUrl = baseUrlInput.value.trim().replace(/\/+$/, '');
    let url = `${baseUrl}${endpoint}`;

    const keys = Object.keys(queryParams).filter(k => queryParams[k] !== '' && queryParams[k] !== null && queryParams[k] !== undefined);
    if (keys.length > 0) {
      const qStr = keys.map(k => `${encodeURIComponent(k)}=${encodeURIComponent(queryParams[k])}`).join('&');
      url += `?${qStr}`;
    }

    const options = {
      method,
      headers: getHeaders(),
    };

    if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(body);
    }

    const startTime = performance.now();
    statusBadge.className = 'status-badge';
    statusBadge.textContent = 'PENDING...';
    timeBadge.textContent = '';
    responseBody.textContent = 'Sending request...';

    try {
      const res = await fetch(url, options);
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);

      statusBadge.textContent = `${res.status} ${res.statusText}`;
      if (res.status >= 200 && res.status < 300) {
        statusBadge.className = 'status-badge status-2xx';
      } else if (res.status >= 400 && res.status < 500) {
        statusBadge.className = 'status-badge status-4xx';
      } else {
        statusBadge.className = 'status-badge status-5xx';
      }

      timeBadge.textContent = `${duration} ms`;

      let data;
      const contentType = res.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await res.json();
        responseBody.innerHTML = syntaxHighlight(data);
      } else {
        const text = await res.text();
        responseBody.textContent = text || `(No Content - Status ${res.status})`;
      }
      return { status: res.status, data };
    } catch (err) {
      const endTime = performance.now();
      statusBadge.className = 'status-badge status-5xx';
      statusBadge.textContent = 'NETWORK ERROR';
      timeBadge.textContent = `${Math.round(endTime - startTime)} ms`;
      responseBody.textContent = `Error: ${err.message}\nCheck if backend is running at ${url}`;
      return { status: 500, error: err.message };
    }
  }

  function syntaxHighlight(json) {
    if (typeof json !== 'string') {
      json = JSON.stringify(json, null, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-0]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      let cls = 'json-number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key';
        } else {
          cls = 'json-string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-bool';
      } else if (/null/.test(match)) {
        cls = 'json-null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
    });
  }

  // Render Section Forms
  function renderSection(section) {
    switch (section) {
      case 'auth-hub':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Firebase Authentication Hub</h2>
            <p class="card-desc">Sign in with Google or Email/Password to retrieve a verified Firebase Auth Token & UID.</p>

            <div class="auth-box">
              <button id="googleSignInBtn" class="google-btn">
                <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.6 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.2 8.9 5 12 5z"/><path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"/><path fill="#FBBC05" d="M5.3 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.6 7.4C.6 9.4 0 10.6 0 12.3s.6 2.9 1.6 4.9l3.7-2.4z"/><path fill="#34A853" d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.2-6.7-5.3L1.6 16C3.5 19.8 7.4 23 12 23z"/></svg>
                Continue with Google
              </button>

              <div class="divider-text">OR EMAIL & PASSWORD</div>

              <div class="form-grid">
                <div class="form-group full-span"><label>Email Address</label><input type="email" id="authEmail" placeholder="user@example.com" /></div>
                <div class="form-group full-span"><label>Password</label><input type="password" id="authPass" placeholder="••••••••" /></div>
              </div>

              <div style="display:flex; gap:10px; margin-top:16px;">
                <button id="emailSignUpBtn" class="send-btn" style="flex:1;">Sign Up</button>
                <button id="emailSignInBtn" class="send-btn" style="flex:1; background:#2e3347;">Sign In</button>
              </div>
            </div>

            <div class="section-divider">Current Auth Info</div>
            <div id="authDebugInfo" style="font-family:var(--mono); font-size:12px; color:var(--text-secondary); background:var(--bg-input); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border); white-space:pre-wrap;">
${currentUser ? `UID: ${currentUser.uid}\nEmail: ${currentUser.email}\nEmail Verified: ${currentUser.emailVerified}` : `ℹ️ To use real Google Sign-In, click "Edit" under 🔥 Firebase Config in the top-left sidebar and enter your Firebase Web API Key (AIzaSy...).\n\n💡 Or toggle "Use Mock UID Instead" in the sidebar to bypass live authentication for local testing.`}
            </div>
          </div>`;

        getEl('googleSignInBtn').onclick = () => {
          const provider = new firebase.auth.GoogleAuthProvider();
          firebase.auth().signInWithPopup(provider)
            .then(res => {
              showToast(`Logged in as ${res.user.displayName}`);
              renderSection('auth-hub');
            })
            .catch(err => {
              console.error('Google Sign-In Error:', err);
              if (err.code === 'auth/api-key-not-valid' || (err.message && err.message.includes('API key'))) {
                showToast('❌ Invalid Firebase API Key! Click "Edit" under 🔥 Firebase Config to set your Web API Key, or enable "Use Mock UID Instead".');
                const debugEl = getEl('authDebugInfo');
                if (debugEl) {
                  debugEl.innerHTML = `<span style="color:var(--red); font-weight:600;">⚠️ Firebase API Key Missing or Invalid</span>\n\nTo use real Google Sign-In:\n1. Click "Edit" under 🔥 Firebase Config in the top-left sidebar.\n2. Enter your Firebase Web API Key (starts with AIzaSy...).\n3. Click "Initialize Firebase".\n\nAlternatively, enable "Use Mock UID Instead" in the sidebar for instant local testing without Google credentials!`;
                }
              } else {
                showToast(`Google Sign-In error: ${err.message}`);
              }
            });
        };

        getEl('emailSignUpBtn').onclick = () => {
          const email = getEl('authEmail').value.trim();
          const pass = getEl('authPass').value;
          if (!email || !pass) return showToast('Email and password required');
          firebase.auth().createUserWithEmailAndPassword(email, pass)
            .then(res => {
              showToast(`Account created for ${res.user.email}`);
              renderSection('auth-hub');
            })
            .catch(err => showToast(`Sign Up Error: ${err.message}`));
        };

        getEl('emailSignInBtn').onclick = () => {
          const email = getEl('authEmail').value.trim();
          const pass = getEl('authPass').value;
          if (!email || !pass) return showToast('Email and password required');
          firebase.auth().signInWithEmailAndPassword(email, pass)
            .then(res => {
              showToast(`Welcome back ${res.user.email}`);
              renderSection('auth-hub');
            })
            .catch(err => showToast(`Sign In Error: ${err.message}`));
        };
        break;

      case 'onboarding-client':
        const activeClientUid = currentUser ? currentUser.uid : (getEl('mockUid').value || 'client-001');
        const activeClientEmail = currentUser ? currentUser.email : 'client@example.com';
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Client Onboarding & Profile Setup</h2>
            <p class="card-desc">Save client details to Firestore and sync profile with Fiti backend.</p>

            <div class="form-grid">
              <div class="form-group full-span">
                <label>Firebase Auth UID</label>
                <input type="text" id="clientUid" value="${activeClientUid}" />
              </div>
              <div class="form-group"><label>Full Name</label><input type="text" id="clientName" value="${currentUser ? (currentUser.displayName || 'Client User') : 'John Client'}" /></div>
              <div class="form-group"><label>Email</label><input type="email" id="clientEmail" value="${activeClientEmail}" /></div>

              <div class="section-divider full-span">Body Measurements (Inches / cm)</div>
              <div class="form-group"><label>Chest</label><input type="number" step="0.5" id="cChest" value="38" /></div>
              <div class="form-group"><label>Waist</label><input type="number" step="0.5" id="cWaist" value="32" /></div>
              <div class="form-group"><label>Shoulder</label><input type="number" step="0.5" id="cShoulder" value="18" /></div>
              <div class="form-group"><label>Sleeve</label><input type="number" step="0.5" id="cSleeve" value="25" /></div>
              <div class="form-group"><label>Neck</label><input type="number" step="0.5" id="cNeck" value="15.5" /></div>
              <div class="form-group"><label>Hip</label><input type="number" step="0.5" id="cHip" value="36" /></div>
              <div class="form-group"><label>Inseam</label><input type="number" step="0.5" id="cInseam" value="30" /></div>
              <div class="form-group"><label>Length</label><input type="number" step="0.5" id="cLength" value="40" /></div>
              <div class="form-group full-span"><label>Notes</label><textarea id="cNotes">Prefers slim-fit tailoring.</textarea></div>
            </div>

            <button id="saveClientBtn" class="send-btn">Save to Firestore & Sync Backend</button>
          </div>`;

        getEl('saveClientBtn').onclick = async () => {
          const uid = getEl('clientUid').value.trim();
          const name = getEl('clientName').value.trim();
          const email = getEl('clientEmail').value.trim();

          const measurements = {
            chest: parseFloat(getEl('cChest').value) || null,
            waist: parseFloat(getEl('cWaist').value) || null,
            shoulder: parseFloat(getEl('cShoulder').value) || null,
            sleeve: parseFloat(getEl('cSleeve').value) || null,
            neck: parseFloat(getEl('cNeck').value) || null,
            hip: parseFloat(getEl('cHip').value) || null,
            inseam: parseFloat(getEl('cInseam').value) || null,
            length: parseFloat(getEl('cLength').value) || null,
            notes: getEl('cNotes').value.trim() || null,
          };

          // Step 1: Save to Firestore
          if (db) {
            try {
              await db.collection('users').doc(uid).set({
                uid,
                role: 'client',
                name,
                email,
                measurements,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
              }, { merge: true });
              showToast('Saved client profile in Firestore!');
            } catch (fsErr) {
              console.warn('Firestore write warning:', fsErr.message);
            }
          }

          // Step 2: Register Client in Fiti Backend
          showToast('Registering client in Fiti Backend...');
          const regRes = await makeRequest('POST', '/profiles/client', { id: uid });

          // Step 3: Save Measurements in Fiti Backend
          if (regRes.status < 400 || regRes.status === 409) {
            showToast('Saving measurements in Fiti Backend...');
            await makeRequest('PUT', `/profiles/client/${uid}/measurements`, measurements);
          }
        };
        break;

      case 'onboarding-seller':
        const activeSellerUid = currentUser ? currentUser.uid : (getEl('mockUid').value || 'seller-001');
        const activeSellerEmail = currentUser ? currentUser.email : 'seller@example.com';
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Seller Onboarding & Shop Setup</h2>
            <p class="card-desc">Save seller details to Firestore and create seller profile + shop in Fiti backend.</p>

            <div class="form-grid">
              <div class="form-group full-span">
                <label>Firebase Auth UID</label>
                <input type="text" id="sellerUid" value="${activeSellerUid}" />
              </div>
              <div class="form-group"><label>Seller Full Name / Owner</label><input type="text" id="sellerName" value="${currentUser ? (currentUser.displayName || 'Seller Owner') : 'Jane Seller'}" /></div>
              <div class="form-group"><label>Email</label><input type="email" id="sellerEmail" value="${activeSellerEmail}" /></div>
              <div class="form-group"><label>NIC Front Photo URL</label><input type="text" id="sNicFront" value="https://storage.googleapis.com/fiti-b0cb2/nic_front.jpg" /></div>
              <div class="form-group"><label>NIC Rear Photo URL</label><input type="text" id="sNicRear" value="https://storage.googleapis.com/fiti-b0cb2/nic_rear.jpg" /></div>

              <div class="section-divider full-span">Shop Details</div>
              <div class="form-group"><label>Shop Name <span>*</span></label><input type="text" id="sShopName" value="Master Tailors Studio" /></div>
              <div class="form-group"><label>Contact Number</label><input type="text" id="sShopContact" value="+94771234567" /></div>
              <div class="form-group full-span"><label>Shop Bio</label><textarea id="sShopBio">High-end bespoke suits, sarees, and custom wedding attire.</textarea></div>
              <div class="form-group"><label>Address</label><input type="text" id="sShopAddr" value="78 Galle Road" /></div>
              <div class="form-group"><label>City</label><input type="text" id="sShopCity" value="Colombo" /></div>
              <div class="form-group"><label>Registration No.</label><input type="text" id="sShopReg" value="REG-SL-9921" /></div>
              <div class="form-group"><label>Latitude</label><input type="number" step="0.0001" id="sShopLat" value="6.9271" /></div>
              <div class="form-group"><label>Longitude</label><input type="number" step="0.0001" id="sShopLng" value="79.8612" /></div>
            </div>

            <button id="saveSellerBtn" class="send-btn">Save to Firestore & Create Shop in Backend</button>
          </div>`;

        getEl('saveSellerBtn').onclick = async () => {
          const uid = getEl('sellerUid').value.trim();
          const name = getEl('sellerName').value.trim();
          const email = getEl('sellerEmail').value.trim();
          const nicFront = getEl('sNicFront').value.trim();
          const nicRear = getEl('sNicRear').value.trim();

          const shopData = {
            seller_id: uid,
            shop_name: getEl('sShopName').value.trim(),
            shop_bio: getEl('sShopBio').value.trim() || null,
            shop_address: getEl('sShopAddr').value.trim() || null,
            city: getEl('sShopCity').value.trim() || null,
            contact_number: getEl('sShopContact').value.trim() || null,
            registration_number: getEl('sShopReg').value.trim() || null,
            latitude: parseFloat(getEl('sShopLat').value) || null,
            longitude: parseFloat(getEl('sShopLng').value) || null,
          };

          // Step 1: Save to Firestore
          if (db) {
            try {
              await db.collection('users').doc(uid).set({
                uid,
                role: 'seller',
                name,
                email,
                nicFront,
                nicRear,
                shop: shopData,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
              }, { merge: true });
              showToast('Saved seller profile in Firestore!');
            } catch (fsErr) {
              console.warn('Firestore write warning:', fsErr.message);
            }
          }

          // Step 2: Register Seller Profile in Fiti Backend
          showToast('Registering seller profile in backend...');
          await makeRequest('POST', '/profiles/seller', {
            id: uid,
            nic_front: nicFront || null,
            nic_rear: nicRear || null,
          });

          // Step 3: Create Shop in Fiti Backend
          showToast('Creating shop in backend...');
          await makeRequest('POST', '/shops/', shopData);
        };
        break;

      case 'health':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Health Check</h2>
            <p class="card-desc">Verify that the FastAPI service is running and healthy.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /health</div>
            <div>
              <button id="sendBtn" class="send-btn">Send Request</button>
            </div>
          </div>`;
        getEl('sendBtn').onclick = () => makeRequest('GET', '/health');
        break;

      case 'client':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Register Client Profile</h2>
            <p class="card-desc">Register a new client profile for an authenticated Firebase user.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /profiles/client</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Client ID (Optional if Bearer Token given)</label>
                <input type="text" id="reqId" placeholder="firebase_uid_123" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Register Client</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const idVal = getEl('reqId').value.trim();
          makeRequest('POST', '/profiles/client', idVal ? { id: idVal } : {});
        };
        break;

      case 'seller':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Register Seller Profile</h2>
            <p class="card-desc">Register a seller/tailor profile with identity verification documents.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /profiles/seller</div>
            <div class="form-grid">
              <div class="form-group full-span">
                <label>Seller ID (Optional if Bearer Token given)</label>
                <input type="text" id="reqId" placeholder="firebase_uid_seller123" />
              </div>
              <div class="form-group">
                <label>NIC Front Image URL</label>
                <input type="text" id="nicFront" placeholder="https://storage.googleapis.com/..." />
              </div>
              <div class="form-group">
                <label>NIC Rear Image URL</label>
                <input type="text" id="nicRear" placeholder="https://storage.googleapis.com/..." />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Register Seller</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {};
          if (getEl('reqId').value.trim()) body.id = getEl('reqId').value.trim();
          if (getEl('nicFront').value.trim()) body.nic_front = getEl('nicFront').value.trim();
          if (getEl('nicRear').value.trim()) body.nic_rear = getEl('nicRear').value.trim();
          makeRequest('POST', '/profiles/seller', body);
        };
        break;

      case 'measurements':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Client Body Measurements</h2>
            <p class="card-desc">Upsert or fetch body measurements for a client profile.</p>
            <div class="endpoint-tag">
              <span class="method-badge PUT">PUT</span>
              <span class="method-badge GET">GET</span>
              /profiles/client/{client_id}/measurements
            </div>
            <div class="form-grid">
              <div class="form-group full-span">
                <label>Client ID <span>*</span></label>
                <input type="text" id="clientId" value="client-001" />
              </div>
              <div class="section-divider full-span">Measurement Tokens</div>
              <div class="form-group"><label>Chest</label><input type="number" step="0.1" id="mChest" value="38.5" /></div>
              <div class="form-group"><label>Waist</label><input type="number" step="0.1" id="mWaist" value="32.0" /></div>
              <div class="form-group"><label>Shoulder</label><input type="number" step="0.1" id="mShoulder" value="18.0" /></div>
              <div class="form-group"><label>Sleeve</label><input type="number" step="0.1" id="mSleeve" value="25.0" /></div>
              <div class="form-group"><label>Neck</label><input type="number" step="0.1" id="mNeck" value="15.5" /></div>
              <div class="form-group"><label>Hip</label><input type="number" step="0.1" id="mHip" value="36.0" /></div>
              <div class="form-group"><label>Inseam</label><input type="number" step="0.1" id="mInseam" value="30.0" /></div>
              <div class="form-group"><label>Length</label><input type="number" step="0.1" id="mLength" value="40.0" /></div>
              <div class="form-group full-span"><label>Notes</label><textarea id="mNotes" placeholder="Slim fit preferred"></textarea></div>
            </div>
            <div style="display:flex; gap:12px;">
              <button id="saveBtn" class="send-btn">Save Measurements (PUT)</button>
              <button id="getBtn" class="send-btn" style="background:#2e3347">Get Measurements (GET)</button>
            </div>
          </div>`;
        getEl('saveBtn').onclick = () => {
          const clientId = getEl('clientId').value.trim();
          if (!clientId) return showToast('Client ID is required');
          const body = {
            chest: parseFloat(getEl('mChest').value) || null,
            waist: parseFloat(getEl('mWaist').value) || null,
            shoulder: parseFloat(getEl('mShoulder').value) || null,
            sleeve: parseFloat(getEl('mSleeve').value) || null,
            neck: parseFloat(getEl('mNeck').value) || null,
            hip: parseFloat(getEl('mHip').value) || null,
            inseam: parseFloat(getEl('mInseam').value) || null,
            length: parseFloat(getEl('mLength').value) || null,
            notes: getEl('mNotes').value.trim() || null,
          };
          makeRequest('PUT', `/profiles/client/${clientId}/measurements`, body);
        };
        getEl('getBtn').onclick = () => {
          const clientId = getEl('clientId').value.trim();
          if (!clientId) return showToast('Client ID is required');
          makeRequest('GET', `/profiles/client/${clientId}/measurements`);
        };
        break;

      case 'shop-create':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Create Shop</h2>
            <p class="card-desc">Create a tailor shop profile linked to a seller ID.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /shops/</div>
            <div class="form-grid">
              <div class="form-group"><label>Seller ID <span>*</span></label><input type="text" id="sellerId" value="seller-001" /></div>
              <div class="form-group"><label>Shop Name <span>*</span></label><input type="text" id="shopName" value="Royal Couture Tailors" /></div>
              <div class="form-group full-span"><label>Shop Bio</label><textarea id="shopBio">Bespoke suit and traditional wear specialists</textarea></div>
              <div class="form-group"><label>Address</label><input type="text" id="shopAddr" value="123 Main Street" /></div>
              <div class="form-group"><label>City</label><input type="text" id="shopCity" value="Colombo" /></div>
              <div class="form-group"><label>Contact Number</label><input type="text" id="shopContact" value="+94771234567" /></div>
              <div class="form-group"><label>Registration No.</label><input type="text" id="shopReg" value="REG-2026-88" /></div>
              <div class="form-group"><label>Latitude</label><input type="number" step="0.0001" id="shopLat" value="6.9271" /></div>
              <div class="form-group"><label>Longitude</label><input type="number" step="0.0001" id="shopLng" value="79.8612" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Create Shop</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            seller_id: getEl('sellerId').value.trim(),
            shop_name: getEl('shopName').value.trim(),
            shop_bio: getEl('shopBio').value.trim() || null,
            shop_address: getEl('shopAddr').value.trim() || null,
            city: getEl('shopCity').value.trim() || null,
            contact_number: getEl('shopContact').value.trim() || null,
            registration_number: getEl('shopReg').value.trim() || null,
            latitude: parseFloat(getEl('shopLat').value) || null,
            longitude: parseFloat(getEl('shopLng').value) || null,
          };
          makeRequest('POST', '/shops/', body);
        };
        break;

      case 'shop-list':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List All Shops</h2>
            <p class="card-desc">Retrieve a paginated list of shops with optional city filtering.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /shops/</div>
            <div class="form-grid">
              <div class="form-group"><label>Skip</label><input type="number" id="skip" value="0" /></div>
              <div class="form-group"><label>Limit</label><input type="number" id="limit" value="100" /></div>
              <div class="form-group full-span"><label>City (Optional)</label><input type="text" id="city" placeholder="Colombo" /></div>
            </div>
            <button id="sendBtn" class="send-btn">List Shops</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const skip = getEl('skip').value;
          const limit = getEl('limit').value;
          const city = getEl('city').value.trim();
          makeRequest('GET', '/shops/', null, { skip, limit, city });
        };
        break;

      case 'shop-get':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Get Shop Details</h2>
            <p class="card-desc">Fetch shop details by unique Shop ID.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /shops/{shop_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Shop ID <span>*</span></label>
                <input type="number" id="shopId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Get Shop</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('shopId').value;
          if (!id) return showToast('Shop ID is required');
          makeRequest('GET', `/shops/${id}`);
        };
        break;

      case 'shop-nearby':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Search Nearby Shops</h2>
            <p class="card-desc">Find tailor shops within a specified GPS radius (km).</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /shops/nearby</div>
            <div class="form-grid">
              <div class="form-group"><label>Latitude <span>*</span></label><input type="number" step="0.0001" id="lat" value="6.9271" /></div>
              <div class="form-group"><label>Longitude <span>*</span></label><input type="number" step="0.0001" id="lng" value="79.8612" /></div>
              <div class="form-group full-span"><label>Radius (km)</label><input type="number" step="0.5" id="radius" value="10.0" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Search Nearby</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const lat = getEl('lat').value;
          const lng = getEl('lng').value;
          const radius_km = getEl('radius').value;
          makeRequest('GET', '/shops/nearby', null, { lat, lng, radius_km });
        };
        break;

      case 'shop-seller':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Get Shops by Seller</h2>
            <p class="card-desc">Fetch all shops registered under a specific seller UID.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /shops/seller/{seller_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Seller ID <span>*</span></label>
                <input type="text" id="sellerId" value="seller-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Shops</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('sellerId').value.trim();
          if (!id) return showToast('Seller ID is required');
          makeRequest('GET', `/shops/seller/${id}`);
        };
        break;

      case 'shop-update':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Update Shop</h2>
            <p class="card-desc">Update shop details by Shop ID.</p>
            <div class="endpoint-tag"><span class="method-badge PUT">PUT</span> /shops/{shop_id}</div>
            <div class="form-grid">
              <div class="form-group full-span"><label>Shop ID <span>*</span></label><input type="number" id="shopId" value="1" /></div>
              <div class="form-group"><label>Shop Name <span>*</span></label><input type="text" id="shopName" value="Royal Couture Tailors Updated" /></div>
              <div class="form-group"><label>City</label><input type="text" id="shopCity" value="Colombo" /></div>
              <div class="form-group full-span"><label>Shop Bio</label><textarea id="shopBio">Updated bio information...</textarea></div>
              <div class="form-group"><label>Address</label><input type="text" id="shopAddr" value="456 New Galle Rd" /></div>
              <div class="form-group"><label>Contact Number</label><input type="text" id="shopContact" value="+94779998888" /></div>
              <div class="form-group"><label>Registration No.</label><input type="text" id="shopReg" value="REG-2026-88" /></div>
              <div class="form-group"><label>Latitude</label><input type="number" step="0.0001" id="shopLat" value="6.9271" /></div>
              <div class="form-group"><label>Longitude</label><input type="number" step="0.0001" id="shopLng" value="79.8612" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Update Shop</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const shopId = getEl('shopId').value;
          if (!shopId) return showToast('Shop ID is required');
          const body = {
            shop_name: getEl('shopName').value.trim(),
            shop_bio: getEl('shopBio').value.trim() || null,
            shop_address: getEl('shopAddr').value.trim() || null,
            city: getEl('shopCity').value.trim() || null,
            contact_number: getEl('shopContact').value.trim() || null,
            registration_number: getEl('shopReg').value.trim() || null,
            latitude: parseFloat(getEl('shopLat').value) || null,
            longitude: parseFloat(getEl('shopLng').value) || null,
          };
          makeRequest('PUT', `/shops/${shopId}`, body);
        };
        break;

      case 'shop-delete':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Delete Shop</h2>
            <p class="card-desc">Permanently delete a shop profile by Shop ID.</p>
            <div class="endpoint-tag"><span class="method-badge DELETE">DELETE</span> /shops/{shop_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Shop ID <span>*</span></label>
                <input type="number" id="shopId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn" style="background:linear-gradient(135deg, #ef4444, #f87171)">Delete Shop</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('shopId').value;
          if (!id) return showToast('Shop ID is required');
          makeRequest('DELETE', `/shops/${id}`);
        };
        break;

      case 'shop-image':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Add Shop Image</h2>
            <p class="card-desc">Attach a showcase photo URL to a shop.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /shops/{shop_id}/images</div>
            <div class="form-grid">
              <div class="form-group"><label>Shop ID <span>*</span></label><input type="number" id="shopId" value="1" /></div>
              <div class="form-group"><label>Image URL <span>*</span></label><input type="text" id="imgUrl" value="https://images.unsplash.com/photo-1593030761757-71fae45fa0e7" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Add Image</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const shopId = getEl('shopId').value;
          const url = getEl('imgUrl').value.trim();
          if (!shopId || !url) return showToast('Shop ID and Image URL are required');
          makeRequest('POST', `/shops/${shopId}/images`, null, { image_url: url });
        };
        break;

      case 'clothing-request':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Create Clothing Request</h2>
            <p class="card-desc">Post a custom tailoring job request to the marketplace or specific shops.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /orders/requests</div>
            <div class="form-grid">
              <div class="form-group"><label>Client ID <span>*</span></label><input type="text" id="reqClient" value="client-001" /></div>
              <div class="form-group"><label>Clothing Category</label><input type="text" id="reqCategory" value="Suit" placeholder="Suit, Dress, Shirt..." /></div>
              <div class="form-group"><label>Target Budget ($)</label><input type="number" step="10" id="reqBudget" value="150" /></div>
              <div class="form-group"><label>Target Date</label><input type="date" id="reqDate" value="2026-08-30" /></div>
              <div class="form-group">
                <label>Gender</label>
                <select id="reqGender">
                  <option value="">(Select)</option>
                  <option value="male" selected>Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label>Fabric Status</label>
                <select id="reqFabric">
                  <option value="provided_by_client" selected>Provided by Client</option>
                  <option value="source_by_seller">Source by Seller</option>
                </select>
              </div>
              <div class="form-group">
                <label>Service Type</label>
                <select id="reqService">
                  <option value="online" selected>Online</option>
                  <option value="physical_visit">Physical Visit</option>
                </select>
              </div>
              <div class="form-group"><label>Location</label><input type="text" id="reqLoc" value="Colombo 03" /></div>
              <div class="form-group full-span"><label>Description</label><textarea id="reqDesc">Two-piece Navy Blue Italian wool suit, double-breasted.</textarea></div>
              <div class="form-group full-span"><label>Target Shop IDs (Comma separated for direct shop invites, or empty for open marketplace)</label><input type="text" id="reqShops" placeholder="1, 2" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Post Request</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const shopsInput = getEl('reqShops').value.trim();
          const target_shop_ids = shopsInput ? shopsInput.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)) : null;

          const body = {
            client_id: getEl('reqClient').value.trim(),
            clothing_category: getEl('reqCategory').value.trim() || null,
            target_budget: parseFloat(getEl('reqBudget').value) || null,
            target_date: getEl('reqDate').value || null,
            gender: getEl('reqGender').value || null,
            fabric_status: getEl('reqFabric').value || null,
            service_type: getEl('reqService').value || 'online',
            request_location: getEl('reqLoc').value.trim() || null,
            description: getEl('reqDesc').value.trim() || null,
            target_shop_ids: target_shop_ids,
          };
          makeRequest('POST', '/orders/requests', body);
        };
        break;

      case 'clothing-get':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Get Clothing Request</h2>
            <p class="card-desc">Fetch details of a clothing request by Request ID.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/requests/{request_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Request ID <span>*</span></label>
                <input type="number" id="reqId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Get Request</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('reqId').value;
          if (!id) return showToast('Request ID is required');
          makeRequest('GET', `/orders/requests/${id}`);
        };
        break;

      case 'clothing-client':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List Requests by Client</h2>
            <p class="card-desc">Fetch all clothing requests created by a specific client.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/requests/client/{client_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Client ID <span>*</span></label>
                <input type="text" id="clientId" value="client-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Client Requests</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('clientId').value.trim();
          if (!id) return showToast('Client ID is required');
          makeRequest('GET', `/orders/requests/client/${id}`);
        };
        break;

      case 'clothing-open':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Open Requests Marketplace</h2>
            <p class="card-desc">List all open clothing requests available for tailors/sellers to bid on.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/requests/open</div>
            <div class="form-grid">
              <div class="form-group"><label>Skip</label><input type="number" id="skip" value="0" /></div>
              <div class="form-group"><label>Limit</label><input type="number" id="limit" value="100" /></div>
            </div>
            <button id="sendBtn" class="send-btn">List Open Requests</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const skip = getEl('skip').value;
          const limit = getEl('limit').value;
          makeRequest('GET', '/orders/requests/open', null, { skip, limit });
        };
        break;

      case 'shop-requests':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List Shop Requests</h2>
            <p class="card-desc">List all shop requests assigned to a specific shop.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/shop-requests/shop/{shop_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Shop ID <span>*</span></label>
                <input type="number" id="shopId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Shop Requests</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('shopId').value;
          if (!id) return showToast('Shop ID is required');
          makeRequest('GET', `/orders/shop-requests/shop/${id}`);
        };
        break;

      case 'bid-submit':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Submit Bid</h2>
            <p class="card-desc">Tailor submits a price bid for a specific shop request.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /orders/bids</div>
            <div class="form-grid">
              <div class="form-group"><label>Shop Request ID <span>*</span></label><input type="number" id="srId" value="1" /></div>
              <div class="form-group"><label>Bid Amount ($) <span>*</span></label><input type="number" step="5" id="bidAmount" value="140.00" /></div>
              <div class="form-group full-span"><label>Message</label><textarea id="bidMsg">We can finish this within 5 business days using premium Italian wool.</textarea></div>
            </div>
            <button id="sendBtn" class="send-btn">Submit Bid</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            shop_request_id: parseInt(getEl('srId').value),
            bid_amount: parseFloat(getEl('bidAmount').value),
            message: getEl('bidMsg').value.trim() || null,
          };
          makeRequest('POST', '/orders/bids', body);
        };
        break;

      case 'order-accept':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Accept Bid & Create Order</h2>
            <p class="card-desc">Client accepts a tailor's bid to formalize an active order.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /orders/accept-bid</div>
            <div class="form-grid">
              <div class="form-group"><label>Shop Request ID <span>*</span></label><input type="number" id="srId" value="1" /></div>
              <div class="form-group"><label>Accepted Price ($) <span>*</span></label><input type="number" step="5" id="acceptedPrice" value="140.00" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Accept Bid & Create Order</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            shop_request_id: parseInt(getEl('srId').value),
            accepted_price: parseFloat(getEl('acceptedPrice').value),
          };
          makeRequest('POST', '/orders/accept-bid', body);
        };
        break;

      case 'order-get':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Get Order Details</h2>
            <p class="card-desc">Fetch order status and pricing details by Order ID.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/{order_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Order ID <span>*</span></label>
                <input type="number" id="orderId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Get Order</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('orderId').value;
          if (!id) return showToast('Order ID is required');
          makeRequest('GET', `/orders/${id}`);
        };
        break;

      case 'order-shop':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List Orders by Shop</h2>
            <p class="card-desc">Fetch all active and completed orders for a shop.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/shop/{shop_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Shop ID <span>*</span></label>
                <input type="number" id="shopId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Shop Orders</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('shopId').value;
          if (!id) return showToast('Shop ID is required');
          makeRequest('GET', `/orders/shop/${id}`);
        };
        break;

      case 'order-client':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List Orders by Client</h2>
            <p class="card-desc">Fetch all orders placed by a specific client.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /orders/client/{client_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Client ID <span>*</span></label>
                <input type="text" id="clientId" value="client-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Client Orders</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('clientId').value.trim();
          if (!id) return showToast('Client ID is required');
          makeRequest('GET', `/orders/client/${id}`);
        };
        break;

      case 'order-status':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Update Order Status</h2>
            <p class="card-desc">Advance order status through the tailoring workflow pipeline.</p>
            <div class="endpoint-tag"><span class="method-badge PATCH">PATCH</span> /orders/{order_id}/status</div>
            <div class="form-grid">
              <div class="form-group"><label>Order ID <span>*</span></label><input type="number" id="orderId" value="1" /></div>
              <div class="form-group">
                <label>Order Status <span>*</span></label>
                <select id="orderStatus">
                  <option value="pending">pending</option>
                  <option value="in_progress">in_progress</option>
                  <option value="completed">completed</option>
                  <option value="cancelled">cancelled</option>
                </select>
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Update Status</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const orderId = getEl('orderId').value;
          const status = getEl('orderStatus').value;
          if (!orderId) return showToast('Order ID is required');
          makeRequest('PATCH', `/orders/${orderId}/status`, null, { order_status: status });
        };
        break;

      case 'payment':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Process Mock Payment</h2>
            <p class="card-desc">Simulate a payment transaction for an active order.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /orders/payments/mock</div>
            <div class="form-grid">
              <div class="form-group"><label>Order ID <span>*</span></label><input type="number" id="orderId" value="1" /></div>
              <div class="form-group"><label>Amount ($) <span>*</span></label><input type="number" step="5" id="amount" value="140.00" /></div>
              <div class="form-group full-span">
                <label>Payment Method</label>
                <select id="payMethod">
                  <option value="card" selected>Credit / Debit Card</option>
                  <option value="cash">Cash on Delivery</option>
                  <option value="online_transfer">Online Bank Transfer</option>
                </select>
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Process Mock Payment</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            order_id: parseInt(getEl('orderId').value),
            amount: parseFloat(getEl('amount').value),
            payment_method: getEl('payMethod').value,
          };
          makeRequest('POST', '/orders/payments/mock', body);
        };
        break;

      case 'rating':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Submit Shop Rating</h2>
            <p class="card-desc">Client submits a review and star rating (1-5) for a completed order.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /orders/ratings</div>
            <div class="form-grid">
              <div class="form-group"><label>Order ID <span>*</span></label><input type="number" id="orderId" value="1" /></div>
              <div class="form-group"><label>Shop ID <span>*</span></label><input type="number" id="shopId" value="1" /></div>
              <div class="form-group"><label>Client ID <span>*</span></label><input type="text" id="clientId" value="client-001" /></div>
              <div class="form-group">
                <label>Rating (1 - 5) <span>*</span></label>
                <select id="ratingVal">
                  <option value="5" selected>5 Stars - Outstanding</option>
                  <option value="4">4 Stars - Very Good</option>
                  <option value="3">3 Stars - Average</option>
                  <option value="2">2 Stars - Poor</option>
                  <option value="1">1 Star - Terrible</option>
                </select>
              </div>
              <div class="form-group full-span"><label>Review</label><textarea id="reviewText">Excellent craftsmanship and fits perfectly! Highly recommended.</textarea></div>
            </div>
            <button id="sendBtn" class="send-btn">Submit Rating</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            order_id: parseInt(getEl('orderId').value),
            shop_id: parseInt(getEl('shopId').value),
            client_id: getEl('clientId').value.trim(),
            rating: parseInt(getEl('ratingVal').value),
            review: getEl('reviewText').value.trim() || null,
          };
          makeRequest('POST', '/orders/ratings', body);
        };
        break;

      case 'notif-create':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Create Notification</h2>
            <p class="card-desc">Send a user notification message.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /support/notifications</div>
            <div class="form-grid">
              <div class="form-group"><label>User ID <span>*</span></label><input type="text" id="userId" value="client-001" /></div>
              <div class="form-group"><label>Title <span>*</span></label><input type="text" id="notifTitle" value="Order Update" /></div>
              <div class="form-group full-span"><label>Message</label><textarea id="notifMsg">Your suit fitting is scheduled for tomorrow at 3 PM.</textarea></div>
            </div>
            <button id="sendBtn" class="send-btn">Create Notification</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            user_id: getEl('userId').value.trim(),
            title: getEl('notifTitle').value.trim(),
            message: getEl('notifMsg').value.trim() || null,
          };
          makeRequest('POST', '/support/notifications', body);
        };
        break;

      case 'notif-list':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List User Notifications</h2>
            <p class="card-desc">Fetch all notifications for a specific user ID.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /support/notifications/{user_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>User ID <span>*</span></label>
                <input type="text" id="userId" value="client-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Notifications</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('userId').value.trim();
          if (!id) return showToast('User ID is required');
          makeRequest('GET', `/support/notifications/${id}`);
        };
        break;

      case 'notif-read':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Mark Notification Read</h2>
            <p class="card-desc">Mark a specific notification as read by Notification ID.</p>
            <div class="endpoint-tag"><span class="method-badge PATCH">PATCH</span> /support/notifications/{id}/read</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Notification ID <span>*</span></label>
                <input type="number" id="notifId" value="1" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Mark Read</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('notifId').value;
          if (!id) return showToast('Notification ID is required');
          makeRequest('PATCH', `/support/notifications/${id}/read`);
        };
        break;

      case 'fav-add':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Add Favorite Shop</h2>
            <p class="card-desc">Add a shop to client's favorites list.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /support/favorites</div>
            <div class="form-grid">
              <div class="form-group"><label>Client ID <span>*</span></label><input type="text" id="clientId" value="client-001" /></div>
              <div class="form-group"><label>Shop ID <span>*</span></label><input type="number" id="shopId" value="1" /></div>
            </div>
            <button id="sendBtn" class="send-btn">Add Favorite</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            client_id: getEl('clientId').value.trim(),
            shop_id: parseInt(getEl('shopId').value),
          };
          makeRequest('POST', '/support/favorites', body);
        };
        break;

      case 'fav-remove':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Remove Favorite Shop</h2>
            <p class="card-desc">Remove a shop from client's favorites list.</p>
            <div class="endpoint-tag"><span class="method-badge DELETE">DELETE</span> /support/favorites/{client_id}/{shop_id}</div>
            <div class="form-grid">
              <div class="form-group"><label>Client ID <span>*</span></label><input type="text" id="clientId" value="client-001" /></div>
              <div class="form-group"><label>Shop ID <span>*</span></label><input type="number" id="shopId" value="1" /></div>
            </div>
            <button id="sendBtn" class="send-btn" style="background:linear-gradient(135deg, #ef4444, #f87171)">Remove Favorite</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const clientId = getEl('clientId').value.trim();
          const shopId = getEl('shopId').value;
          if (!clientId || !shopId) return showToast('Client ID and Shop ID are required');
          makeRequest('DELETE', `/support/favorites/${clientId}/${shopId}`);
        };
        break;

      case 'fav-list':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">List Favorite Shops</h2>
            <p class="card-desc">Fetch all favorite shops saved by a client.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /support/favorites/{client_id}</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>Client ID <span>*</span></label>
                <input type="text" id="clientId" value="client-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Favorites</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('clientId').value.trim();
          if (!id) return showToast('Client ID is required');
          makeRequest('GET', `/support/favorites/${id}`);
        };
        break;

      case 'rbac-assign':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Assign User Role</h2>
            <p class="card-desc">Assign RBAC role (e.g. client, seller, admin) to a user UID.</p>
            <div class="endpoint-tag"><span class="method-badge POST">POST</span> /rbac/assign-role</div>
            <div class="form-grid">
              <div class="form-group"><label>User ID <span>*</span></label><input type="text" id="userId" value="client-001" /></div>
              <div class="form-group">
                <label>Role Name <span>*</span></label>
                <select id="roleName">
                  <option value="client" selected>client</option>
                  <option value="seller">seller</option>
                  <option value="admin">admin</option>
                </select>
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Assign Role</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const body = {
            user_id: getEl('userId').value.trim(),
            role_name: getEl('roleName').value,
          };
          makeRequest('POST', '/rbac/assign-role', body);
        };
        break;

      case 'rbac-access':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Get User Access Overview</h2>
            <p class="card-desc">Retrieve a user's assigned roles and accessible sections.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /rbac/users/{user_id}/access</div>
            <div class="form-grid single">
              <div class="form-group">
                <label>User ID <span>*</span></label>
                <input type="text" id="userId" value="client-001" />
              </div>
            </div>
            <button id="sendBtn" class="send-btn">Fetch Access Overview</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const id = getEl('userId').value.trim();
          if (!id) return showToast('User ID is required');
          makeRequest('GET', `/rbac/users/${id}/access`);
        };
        break;

      case 'rbac-check':
        contentArea.innerHTML = `
          <div class="card">
            <h2 class="card-title">Check Route Access</h2>
            <p class="card-desc">Verify whether a user UID has permissions to access a specific route.</p>
            <div class="endpoint-tag"><span class="method-badge GET">GET</span> /rbac/users/{user_id}/check-route</div>
            <div class="form-grid">
              <div class="form-group"><label>User ID <span>*</span></label><input type="text" id="userId" value="client-001" /></div>
              <div class="form-group"><label>Route Name <span>*</span></label><input type="text" id="routeName" value="client_dashboard" placeholder="client_dashboard, shop_manage, etc." /></div>
            </div>
            <button id="sendBtn" class="send-btn">Check Route</button>
          </div>`;
        getEl('sendBtn').onclick = () => {
          const userId = getEl('userId').value.trim();
          const routeName = getEl('routeName').value.trim();
          if (!userId || !routeName) return showToast('User ID and Route Name are required');
          makeRequest('GET', `/rbac/users/${userId}/check-route`, null, { route_name: routeName });
        };
        break;

      default:
        contentArea.innerHTML = `<div class="card"><h2 class="card-title">Select an endpoint from sidebar</h2></div>`;
    }
  }

  // Initial render
  renderSection('auth-hub');
});
