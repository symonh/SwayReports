// Script to populate Firebase with real feedback data
const admin = require('firebase-admin');
const fs = require('fs');

// Load service account credentials from file
const serviceAccount = require('/Users/simon/Documents/GitHub/dashboard-write-db-firebase-adminsdk-fbsvc-15834c79fb.json');

// Initialize Firebase Admin with service account credentials
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: `https://${serviceAccount.project_id}.firebaseio.com`
});

const firestore = admin.firestore();

// Collection paths
const FEEDBACK_COLLECTION = 'feedback';
const CATEGORIES_COLLECTION = 'feedbackCategories';

// Real categories data
const categories = [
  { id: "student-engagement", name: "Student Engagement" },
  { id: "teaching-strategies", name: "Teaching Strategies" },
  { id: "classroom-management", name: "Classroom Management" },
  { id: "lesson-planning", name: "Lesson Planning" },
  { id: "time-management", name: "Time Management" },
  { id: "differentiation", name: "Differentiation" },
  { id: "technology-integration", name: "Technology Integration" },
  { id: "assessment", name: "Assessment & Feedback" },
  { id: "student-motivation", name: "Student Motivation" }
];

// Real feedback data
const feedbackItems = [
  {
    text: "Calling on students by name has dramatically improved classroom engagement. I've noticed significantly higher participation rates since implementing this strategy.",
    categories: ["student-engagement", "teaching-strategies"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Breaking complex activities into smaller timed segments has helped maintain student focus throughout longer lessons. Students report feeling less overwhelmed by difficult material.",
    categories: ["classroom-management", "lesson-planning", "time-management"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Implementing digital exit tickets through Google Forms has provided valuable immediate feedback while reducing paper waste. This has helped me adjust lessons for the next day.",
    categories: ["assessment", "technology-integration"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Creating a tiered assignment system with required and optional components has allowed advanced students to push themselves while ensuring all students meet core requirements.",
    categories: ["differentiation", "student-motivation"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Using the 'think-pair-share' technique has dramatically improved participation from typically quiet students. The structured approach gives them confidence to contribute.",
    categories: ["student-engagement", "teaching-strategies"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Implementing a digital reward system has positively impacted classroom behavior. Students are more motivated to follow procedures and participate actively.",
    categories: ["classroom-management", "student-motivation", "technology-integration"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Providing exemplars of high-quality work has clarified expectations and improved overall assignment quality. Students appreciate seeing concrete examples of success.",
    categories: ["teaching-strategies", "assessment"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Using cooperative learning structures has increased engagement while developing critical social skills. Students report enjoying class more when collaboration is built in.",
    categories: ["student-engagement", "teaching-strategies"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Implementing student choice in project formats has increased motivation and creativity. Students take more ownership when they can play to their strengths.",
    categories: ["differentiation", "student-motivation"],
    createdAt: admin.firestore.Timestamp.now()
  },
  {
    text: "Using quick formative assessments with digital tools has allowed me to identify and address misconceptions in real-time rather than discovering them on major assessments.",
    categories: ["assessment", "technology-integration"],
    createdAt: admin.firestore.Timestamp.now()
  }
];

// Function to add categories to Firestore
async function addCategories() {
  console.log("Adding categories to Firestore...");
  
  const batch = firestore.batch();
  
  categories.forEach(category => {
    const docRef = firestore.collection(CATEGORIES_COLLECTION).doc(category.id);
    batch.set(docRef, { name: category.name });
  });
  
  try {
    await batch.commit();
    console.log(`Successfully added ${categories.length} categories to Firestore.`);
  } catch (error) {
    console.error("Error adding categories:", error);
  }
}

// Function to add feedback items to Firestore
async function addFeedbackItems() {
  console.log("Adding feedback items to Firestore...");
  
  const batch = firestore.batch();
  
  feedbackItems.forEach((item, index) => {
    const docRef = firestore.collection(FEEDBACK_COLLECTION).doc(`feedback-${index + 1}`);
    batch.set(docRef, item);
  });
  
  try {
    await batch.commit();
    console.log(`Successfully added ${feedbackItems.length} feedback items to Firestore.`);
  } catch (error) {
    console.error("Error adding feedback items:", error);
  }
}

// Main function to populate data
async function populateFirestore() {
  console.log("Starting Firestore population with admin credentials...");
  
  try {
    await addCategories();
    await addFeedbackItems();
    console.log("Firestore population completed successfully!");
  } catch (error) {
    console.error("Error populating Firestore:", error);
  } finally {
    process.exit(0);
  }
}

// Run the script
populateFirestore(); 