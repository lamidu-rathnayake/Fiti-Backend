// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import {
    getAuth,
    signInWithPopup,
    GoogleAuthProvider,
    signOut,
    onAuthStateChanged,
} from "firebase/auth";

// TODO: Replace the following with your app's Firebase project configuration
// See: https://firebase.google.com/docs/web/learn-more#config-object
const firebaseConfig = {
    apiKey: "AIzaSyBGbesTxWPOqshyBogCuUjS8pccJWitTdQ",
    authDomain: "fiti-b0cb2.firebaseapp.com",
    projectId: "fiti-b0cb2",
    storageBucket: "fiti-b0cb2.firebasestorage.app",
    messagingSenderId: "1041965038766",
    appId: "1:1041965038766:web:7b6099b26931c41990c13f",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// DOM Elements
const loginBtn = document.getElementById("google-login-btn");
const logoutBtn = document.getElementById("logout-btn");
const userInfo = document.getElementById("user-info");
const errorMessage = document.getElementById("error-message");

const userNameEl = document.getElementById("user-name");
const userEmailEl = document.getElementById("user-email");
const userPhotoEl = document.getElementById("user-photo");

// Listen for authentication state changes
onAuthStateChanged(auth, (user) => {
    if (user) {
        // User is signed in
        showUserInfo(user);
    } else {
        // User is signed out
        showLoginBtn();
    }
});

// Sign in with Google
loginBtn.addEventListener("click", () => {
    errorMessage.classList.add("hidden");

    signInWithPopup(auth, provider)
        .then((result) => {
            // The signed-in user info.
            const user = result.user;
            showUserInfo(user);
            console.log("Successfully logged in:", user);
        })
        .catch((error) => {
            // Handle Errors here.
            const errorCode = error.code;
            const errorMsg = error.message;
            console.error("Login Error:", errorCode, errorMsg);

            errorMessage.textContent = `Login failed: ${errorMsg}`;
            errorMessage.classList.remove("hidden");
        });
});

// Sign out
logoutBtn.addEventListener("click", () => {
    signOut(auth)
        .then(() => {
            showLoginBtn();
        })
        .catch((error) => {
            console.error("Logout Error:", error);
        });
});

// UI Helper Functions
function showUserInfo(user) {
    loginBtn.classList.add("hidden");
    userInfo.classList.remove("hidden");
    errorMessage.classList.add("hidden");

    userNameEl.textContent = user.displayName;
    userEmailEl.textContent = user.email;
    userPhotoEl.src = user.photoURL || "https://via.placeholder.com/80";
}

function showLoginBtn() {
    loginBtn.classList.remove("hidden");
    userInfo.classList.add("hidden");

    userNameEl.textContent = "";
    userEmailEl.textContent = "";
    userPhotoEl.src = "";
}
