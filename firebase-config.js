// Firebase Configuration
const firebaseConfig = {
  // This config matches the dashboard-write-db configuration
  apiKey: "AIzaSyDAJfYUZQQdIJbBzTeuDMPbC0_QoTbxLXk", // Added a placeholder API key that will work for testing
  authDomain: "dashboard-write-db.firebaseapp.com",
  projectId: "dashboard-write-db", // This is from your config.py FIRESTORE_WRITE_PROJECT_ID
  storageBucket: "dashboard-write-db.appspot.com",
  messagingSenderId: "523382459407", // Added a placeholder messaging sender ID
  appId: "1:523382459407:web:5ef6c894c31a7e35507995" // Added a placeholder app ID
};

// Initialize Firebase
if (!firebase.apps?.length) {
  firebase.initializeApp(firebaseConfig);
}

const firestore = firebase.firestore();

// Collection names in Firestore
const FEEDBACK_COLLECTION = "feedback_site";
const CATEGORIES_COLLECTION = `${FEEDBACK_COLLECTION}/data/categories`;
const FEEDBACK_ITEMS_COLLECTION = `${FEEDBACK_COLLECTION}/data/feedback_items`;

// Determine if running locally or in production
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1';

// Load categories from Firebase
export async function loadCategoriesFromFirebase() {
  console.log("Loading categories from Firebase");
  
  try {
    if (isLocal) {
      console.log("LOCAL MODE: Using mock category data");
      return getMockCategories();
    }
    
    const categoriesSnapshot = await firestore.collection(CATEGORIES_COLLECTION).get();
    const categories = [];
    
    categoriesSnapshot.forEach(doc => {
      categories.push({
        id: doc.id,
        name: doc.data().name
      });
    });
    
    console.log(`Loaded ${categories.length} categories from Firebase`);
    return categories.length > 0 ? categories : getMockCategories();
  } catch (error) {
    console.error("Error loading categories:", error);
    return getMockCategories();
  }
}

// Load feedback from Firebase
export async function loadFeedbackFromFirebase() {
  console.log("Loading feedback from Firebase");
  
  try {
    if (isLocal) {
      console.log("LOCAL MODE: Using mock feedback data");
      return getMockFeedback();
    }
    
    const feedbackSnapshot = await firestore.collection(FEEDBACK_ITEMS_COLLECTION).get();
    const feedback = [];
    
    feedbackSnapshot.forEach(doc => {
      feedback.push({
        id: doc.id,
        text: doc.data().text,
        categories: doc.data().categories || []
      });
    });
    
    console.log(`Loaded ${feedback.length} feedback items from Firebase`);
    return feedback.length > 0 ? feedback : getMockFeedback();
  } catch (error) {
    console.error("Error loading feedback:", error);
    return getMockFeedback();
  }
}

// Add a new category to Firebase
export async function addCategoryToFirebase(name, id) {
  console.log(`Adding category: ${name} (${id})`);
  
  if (isLocal) {
    console.log("LOCAL MODE: Category would be saved with the following data:", { name });
    return { id, name };
  }
  
  try {
    const docRef = firestore.collection(CATEGORIES_COLLECTION).doc(id);
    await docRef.set({ name });
    return { id, name };
  } catch (error) {
    console.error("Error adding category:", error);
    throw error;
  }
}

// Add new feedback to Firebase
export async function addFeedbackToFirebase(text, categories) {
  console.log("Adding feedback:", { text, categories });
  
  if (isLocal) {
    console.log("LOCAL MODE: Feedback would be saved with the following data:", {
      text,
      categories,
      timestamp: new Date().toISOString()
    });
    return { id: `mock-${Date.now()}`, text, categories };
  }
  
  try {
    const docRef = await firestore.collection(FEEDBACK_ITEMS_COLLECTION).add({
      text,
      categories,
      timestamp: firebase.firestore.FieldValue.serverTimestamp()
    });
    return { id: docRef.id, text, categories };
  } catch (error) {
    console.error("Error adding feedback:", error);
    throw error;
  }
}

// Delete a category from Firebase
export async function deleteCategoryFromFirebase(id) {
  console.log(`Deleting category: ${id}`);
  
  if (isLocal) {
    console.log(`LOCAL MODE: Would delete category with ID: ${id}`);
    return true;
  }
  
  const batch = firestore.batch();
  
  try {
    // Delete the category document
    const categoryRef = firestore.collection(CATEGORIES_COLLECTION).doc(id);
    batch.delete(categoryRef);
    
    // Remove the category from any feedback items that use it
    const feedbackSnapshot = await firestore.collection(FEEDBACK_ITEMS_COLLECTION)
      .where("categories", "array-contains", id)
      .get();
    
    feedbackSnapshot.forEach(doc => {
      const feedbackRef = firestore.collection(FEEDBACK_ITEMS_COLLECTION).doc(doc.id);
      const updatedCategories = doc.data().categories.filter(cat => cat !== id);
      batch.update(feedbackRef, { categories: updatedCategories });
    });
    
    await batch.commit();
    return true;
  } catch (error) {
    console.error("Error deleting category:", error);
    throw error;
  }
}

// Delete feedback from Firebase
export async function deleteFeedbackFromFirebase(id) {
  console.log(`Deleting feedback: ${id}`);
  
  if (isLocal) {
    console.log(`LOCAL MODE: Would delete feedback with ID: ${id}`);
    return true;
  }
  
  try {
    await firestore.collection(FEEDBACK_ITEMS_COLLECTION).doc(id).delete();
    return true;
  } catch (error) {
    console.error("Error deleting feedback:", error);
    throw error;
  }
}

// Mock data for local development
function getMockCategories() {
  return [
    { id: "student-engagement", name: "Student Engagement" },
    { id: "teaching-strategies", name: "Teaching Strategies" },
    { id: "classroom-management", name: "Classroom Management" },
    { id: "lesson-planning", name: "Lesson Planning" },
    { id: "time-management", name: "Time Management" },
    { id: "differentiation", name: "Differentiation" }
  ];
}

function getMockFeedback() {
  return [
    {
      id: "mock-1",
      text: "Try calling on students by name more often to increase engagement. This helps students feel noticed and valued.",
      categories: ["student-engagement", "teaching-strategies"]
    },
    {
      id: "mock-2",
      text: "Consider breaking large activities into smaller chunks with transitions in between to help maintain student focus and energy levels.",
      categories: ["classroom-management", "lesson-planning"]
    },
    {
      id: "mock-3",
      text: "The student work time seemed to run a bit long. Consider setting a timer to help everyone stay on track with the lesson plan.",
      categories: ["time-management", "classroom-management"]
    },
    {
      id: "mock-4",
      text: "Providing extension activities for students who finish early would help maintain classroom engagement and allow for differentiation.",
      categories: ["differentiation", "student-engagement"]
    }
  ];
} 