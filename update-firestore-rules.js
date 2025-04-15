// Script to update Firestore security rules
const admin = require('firebase-admin');
const fs = require('fs');

// Load service account credentials from file
const serviceAccount = require('/Users/simon/Documents/GitHub/dashboard-write-db-firebase-adminsdk-fbsvc-15834c79fb.json');

// Initialize Firebase Admin with service account credentials
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: `https://${serviceAccount.project_id}.firebaseio.com`
});

// Get Firestore instance
const firestore = admin.firestore();

// Simple security rules that allow read access but require authentication for writes
const securityRules = {
  rules: `rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow public read access to the feedback and categories collections
    match /${firestore.collection('feedback').path}/{document=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    match /${firestore.collection('feedbackCategories').path}/{document=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    // Default - block everything else
    match /{document=**} {
      allow read, write: if false;
    }
  }
}`
};

// Update Firestore rules using Firebase Admin SDK Project Management API
async function updateFirestoreRules() {
  try {
    console.log("Updating Firestore security rules to allow public read access...");
    
    // This requires Firebase Admin Project Management API, which would normally be used
    // In this case, we'll output instructions for manually updating the rules
    console.log("Security rules to set:");
    console.log("----------------------------------------------");
    console.log(securityRules.rules);
    console.log("----------------------------------------------");
    console.log("\nFirebase Admin SDK doesn't directly support updating security rules via Node.js.");
    console.log("Please update your Firestore security rules manually in the Firebase Console:");
    console.log("1. Go to https://console.firebase.google.com/project/dashboard-write-db/firestore/rules");
    console.log("2. Replace the existing rules with the rules printed above");
    console.log("3. Click 'Publish' to save the changes");
    
  } catch (error) {
    console.error("Error updating Firestore rules:", error);
  } finally {
    process.exit(0);
  }
}

// Run the script
updateFirestoreRules(); 