# AAROHA OS
### AI-Powered Human Operating System

AAROHA OS is a premium, AI-powered health, career, finance, and life companion application. It acts as a single, secure "Human Operating System" layer, integrating local and cloud-based intelligence modules to organize, track, and optimize daily habits, health metrics, career targets, distraction-free study plans, and long-term financial choices. 

The application is built on a responsive mobile architecture using **Flutter** and **Dart** and features a modern **deep space glassmorphism UI** optimized for Android.

---

## 🌟 Key Features

### 👤 Secure Authentication & Session Management
* **Email & Password Login**: Seamless user onboarding with client-side form validation.
* **Google Sign-In**: Integrated secure authentication with Firebase.
* **Forgot Password**: Password reset mail triggering directly via Firebase.
* **Persistent Sessions**: Shared Preferences tracks authentication state so users bypass the login screen after their first login.
* **Modern Glassmorphism UI**: Semi-transparent frost panels, glowing widgets, and custom field styling.

### 💼 Career Brain
* **Resume Builder & Parsing**: Automatically structure profile details and optimize for job screening.
* **Interview Simulator**: Interactive coaching tools mimicking developer/analyst interviews.
* **Skill Gap Analysis**: Visual progress tracker mapping current expertise against target roles (e.g., Senior Data Scientist).
* **Document Hub**: Digital locker for secure local credential and certificate tracking.

### 🎓 Education Brain
* **Focus Mode**: Distraction-free screen block timer supporting pomodoro routines.
* **Learning Twin**: Interactive AI tutor utilizing Gemini and OpenAI models.
* **Study Circle & Planner**: Collaborative notes manager and course planning dashboard.
* **Quiz Engine**: AI-generated quizzes from user notes to test retention.

### 💵 Money Brain
* **Expense Tracker**: Dynamic journaling of daily transaction flows.
* **Investment Simulator**: Mock portfolio tracking and custom asset suggestions.
* **Scam Protection**: AI scanner looking for suspicious messages or transaction alerts.
* **Smart Shopping Assistant**: AI advisor weighing budget constraints against shopping lists.

### 🏃 Health Brain
* **Daily Indicators**: Habit loggers for daily step counts, hydration, exercise routines, and sleep patterns.
* **Health Analytics**: Visual indicators illustrating progress metrics.

### 🧭 Life Brain
* **Daily Briefing**: Contextual morning brief analyzing user profiles to organize priorities.
* **Travel Assistant**: Custom packing list, duration planning, and destination budget estimation.
* **Government Scheme Finder**: Scrapes/analyzes criteria to match eligible state schemes.

---

## 🛠️ Technology Stack

* **Frontend Framework**: [Flutter SDK](https://flutter.dev) (Dart)
* **Backend Services**: [Firebase Authentication](https://firebase.google.com/docs/auth), [Cloud Firestore](https://firebase.google.com/docs/firestore)
* **API Service Gateway**: FastAPI (Python 3.10+)
* **Session Persistence**: Shared Preferences (Local Storage key-value persistence)
* **AI Model Engine**: OpenAI SDK & Groq API Integrations (Llama-3.3-70b-versatile, Gemini)

---

## 📁 Project Architecture & Folder Structure

The project conforms to a clean, domain-grouped modular structure separating core components from screen UI elements:

```
lib/
 ├── core/              # Global constants and shared resources (constants.dart)
 ├── config/            # App routes, initializers, and backend endpoints
 ├── services/          # API gateways, Firebase Authentication, and Firestore services
 ├── models/            # Data entities and parsing models
 ├── providers/         # State management and change notifications
 ├── utils/             # Helper utilities, date formatters, and network interceptors
 ├── widgets/           # Global reusable UI elements (CustomTextField, AuthButton)
 ├── screens/           # Feature-grouped user portals
 │     ├── auth/        # Login, Signup, and Forgot Password screens
 │     ├── home/        # Dashboard view & main navigation portal
 │     ├── career/      # Resume building, skill gap analysis, and document hub
 │     ├── education/   # Focus modes, study planners, and AI learning twins
 │     ├── money/       # Expense tracking, budget goal simulators, and scam protection
 │     ├── health/      # Habits tracking, step logs, and hydration journals
 │     └── life/        # Travel planner, gov scheme finder, and morning briefs
 └── main.dart          # App execution entrypoint & Firebase initializer wrapper
```

---

## 📸 Screenshots

| Modern Glassmorphic Login | Signup Screen | User Dashboard |
| --- | --- | --- |
| ![Login Screenshot Placeholder](https://via.placeholder.com/250x500.png?text=Modern+Login+Screen) | ![Signup Screenshot Placeholder](https://via.placeholder.com/250x500.png?text=Signup+Screen) | ![Dashboard Screenshot Placeholder](https://via.placeholder.com/250x500.png?text=User+Dashboard) |

| Career Brain Profile | Money Brain Expense Tracker | Life Brain Assistant |
| --- | --- | --- |
| ![Career Brain Placeholder](https://via.placeholder.com/250x500.png?text=Career+Brain) | ![Money Brain Placeholder](https://via.placeholder.com/250x500.png?text=Money+Brain) | ![Life Brain Placeholder](https://via.placeholder.com/250x500.png?text=Life+Brain) |

---

## 🔧 Installation & Setup

### 1. Prerequisites
Make sure you have the following installed on your machine:
* [Flutter SDK (Stable Channel)](https://docs.flutter.dev/get-started/install)
* [Android Studio & Android SDK Build-Tools](https://developer.android.com/studio)
* Python 3.10+ (for running the optional Local API Backend)

### 2. Firebase App Configuration
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new Firebase project and register an Android App.
3. Configure the package name to match **`com.aaroha.app`** exactly.
4. Download the generated **`google-services.json`** configuration file.
5. Copy the `google-services.json` file to the Flutter Android module path:
   `aaroha_app/android/app/google-services.json`
6. Run `./gradlew signingReport` in your Android folder, locate your SHA-1 key, and paste it into the Firebase Console Settings to enable **Google Sign-In**.

### 3. Initialize Flutter Project
Inside the `aaroha_app/` directory, install package dependencies:
```bash
flutter pub get
```

### 4. Running the App
Run the application on a connected Android Emulator or physical device:
```bash
flutter run
```

### 5. Build Production Release
To compile the release-ready, optimized APK:
```bash
flutter build apk --release
```
The resulting executable will be stored in:
`build/app/outputs/flutter-apk/app-release.apk`

---

## 🛤️ Future Roadmap

* **On-Device LLMs**: Integrations with Google Gemini Nano for offline advice.
* **Structured Offline Sync**: Automatic offline database (SQLite/Isar) syncing with Cloud Firestore when internet connectivity returns.
* **Wearable Integration**: Integrate health data directly from Google Fit or Samsung Health.
* **AI Career Simulation**: Multi-agent mock interviews simulating strict panel reviews.
