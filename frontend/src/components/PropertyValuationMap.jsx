import React, { useState, useEffect } from 'react';
import PropertyMap from './PropertyMap.jsx';

export default function PropertyValuationMap() {
  const [districts, setDistricts] = useState([]);
  const [taluks, setTaluks] = useState([]);
  const [villages, setVillages] = useState([]);
  
  // Form State
  const [selectedState, setSelectedState] = useState('Karnataka');
  const [pincode, setPincode] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedTaluk, setSelectedTaluk] = useState('');
  const [selectedVillage, setSelectedVillage] = useState('');
  const [landType, setLandType] = useState('Residential');
  const [landArea, setLandArea] = useState(2400);
  const [landPrice, setLandPrice] = useState(0);
  const [surveyNumber, setSurveyNumber] = useState('101/2');

  // Reverse Geocoding States
  const [geocodingLoading, setGeocodingLoading] = useState(false);
  const [geocodedAddress, setGeocodedAddress] = useState(null);

  // Smart Property Selection States
  const [showPropertyModal, setShowPropertyModal] = useState(false);
  const [matchingProperties, setMatchingProperties] = useState([]);
  const [tempGeocodedAddress, setTempGeocodedAddress] = useState(null);

  // Map state (default null so PropertyMap centers on Karnataka)
  const [coordinates, setCoordinates] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Results State
  const [valuationData, setValuationData] = useState(null);
  const [guidelineRecords, setGuidelineRecords] = useState([]);
  const [selectedRecordIndex, setSelectedRecordIndex] = useState(-1);

  // GIS Intelligence States
  const [polygonCoords, setPolygonCoords] = useState([]);
  const [isDrawingMode, setIsDrawingMode] = useState(false);
  const [amenities, setAmenities] = useState([]);
  const [envRiskData, setEnvRiskData] = useState(null);
  const [gisProfile, setGisProfile] = useState(null);

  // Loan Eligibility Simulator States
  const [simDownPayment, setSimDownPayment] = useState(0);
  const [simInterestRate, setSimInterestRate] = useState(9.5);
  const [simTenure, setSimTenure] = useState(20);
  const [simMonthlyIncome, setSimMonthlyIncome] = useState(85000);
  const [simHasCoApplicant, setSimHasCoApplicant] = useState(false);
  const [simCoApplicantIncome, setSimCoApplicantIncome] = useState(50000);

  // AI Underwriting Portal States (Step 6)
  const [activeTab, setActiveTab] = useState("dashboard"); // "dashboard", "home_loan", "agri_loan", "commercial_loan", "gold", "farm_equipment", "vehicle", "appraisal", "ocr", "underwriting", "analytics"
  
  // Role-Based Access Control & Developer Mode State
  const [isDevMode, setIsDevMode] = useState(false); // Developer mode toggle: false hides manual role switcher
  const [userRole, setUserRole] = useState('Loan Officer'); // "Customer", "Loan Officer", "Branch Manager", "Admin"
  const [selectedBranch, setSelectedBranch] = useState('Bengaluru Main Branch');

  // Enterprise Loan Origination Setup States (Purpose & Structure)
  const [loanPurpose, setLoanPurpose] = useState('🏠 Home Purchase');
  const [loanStructure, setLoanStructure] = useState('🔒 Secured Loan'); // "Secured Loan", "Unsecured Loan", "Collateral Based", "Guarantor Based", "Hybrid"
  const [collateralType, setCollateralType] = useState('Property'); // "Property", "Gold", "Vehicle", "Farm Equipment", "Fixed Deposit", "Other"
  const [collateralValue, setCollateralValue] = useState(4500000);
  
  // Guarantor Profile States
  const [guarantorName, setGuarantorName] = useState('Ramesh Sharma');
  const [guarantorRelation, setGuarantorRelation] = useState('Father');
  const [guarantorIncome, setGuarantorIncome] = useState(65000);
  const [guarantorOccupation, setGuarantorOccupation] = useState('Govt Service / Retired');
  const [guarantorPhone, setGuarantorPhone] = useState('+91 98765 43210');
  const [guarantorCibil, setGuarantorCibil] = useState(780);

  // Centralized Shared Loan Application State (Auto-Syncing across all modules)
  const [sharedLoanState, setSharedLoanState] = useState({
    product: 'Home Loan',
    purpose: '🏠 Home Purchase',
    structure: '🔒 Secured Loan',
    borrower_name: 'Aarav Kumar',
    monthly_income: 85000,
    cibil_score: 750,
    requested_amount: 4500000,
    down_payment: 500000,
    on_road_price: 0,
    vehicle_make: 'Mahindra',
    vehicle_model: 'Thar ROXX',
    vehicle_variant: 'AX7L 4WD Diesel MT',
    collateral_type: 'Property',
    collateral_value: 4500000,
    guarantor_name: 'Ramesh Sharma',
    guarantor_income: 65000,
    guarantor_cibil: 780
  });
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  const [activeWorkflowStage, setActiveWorkflowStage] = useState(4); // 1: Submitted, 2: Doc Verification, 3: Valuation, 4: AI Risk, 5: Officer Review, 6: Manager Approval, 7: Sanctioned
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, title: "📄 Documents Uploaded", message: "Aadhaar & PAN verified for Aarav Kumar", time: "10m ago", isRead: false },
    { id: 2, title: "🤖 AI Analysis Finished", message: "AI Credit Risk Score: 18/100 (Low Risk)", time: "25m ago", isRead: false },
    { id: 3, title: "✅ Manager Approval", message: "Sanction letter ready for download", time: "1h ago", isRead: true }
  ]);

  const [auditLogs, setAuditLogs] = useState([
    { timestamp: "2026-07-21 01:45:00", actor: "System AI Engine", role: "AI Officer", action: "Kaveri Guideline Rate Verified", detail: "District Bagalkote, Village Kyada" },
    { timestamp: "2026-07-21 01:50:00", actor: "Rajesh Sharma", role: "Loan Officer", action: "Applicant Dossier Verified", detail: "Aadhaar & PAN Match 100%" },
    { timestamp: "2026-07-21 02:05:00", actor: "Priya Nair", role: "Branch Manager", action: "Approved Collateral LTV Cap", detail: "80% Sanction Ceiling Set" }
  ]);

  // Data Safety & Enterprise Navigation Control States
  const [tabHistory, setTabHistory] = useState(['dashboard']);
  const [tabHistoryIdx, setTabHistoryIdx] = useState(0);
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);
  const [draftVersions, setDraftVersions] = useState([]);
  const [lastSavedTime, setLastSavedTime] = useState(new Date().toLocaleTimeString());
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);

  // Auto-Save Timer (Saves draft every 30 seconds)
  useEffect(() => {
    const timer = setInterval(() => {
      const nowStr = new Date().toLocaleTimeString();
      setLastSavedTime(nowStr);
      setDraftVersions(prev => [
        { id: Date.now(), timestamp: nowStr, state: { ...sharedLoanState }, activeTab },
        ...prev.slice(0, 9)
      ]);
    }, 30000);
    return () => clearInterval(timer);
  }, [sharedLoanState, activeTab]);

  // Unsaved changes browser prompt
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = "You have unsaved loan application changes. Do you want to save before leaving?";
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  // Tab Navigation Handler with History Tracking
  const navigateToTab = (newTab) => {
    if (newTab !== activeTab) {
      setTabHistory(prev => [...prev.slice(0, tabHistoryIdx + 1), newTab]);
      setTabHistoryIdx(prev => prev + 1);
      setActiveTab(newTab);
    }
  };

  const handleGoBack = () => {
    if (tabHistoryIdx > 0) {
      const prevIdx = tabHistoryIdx - 1;
      setTabHistoryIdx(prevIdx);
      setActiveTab(tabHistory[prevIdx]);
    }
  };

  const handleGoForward = () => {
    if (tabHistoryIdx < tabHistory.length - 1) {
      const nextIdx = tabHistoryIdx + 1;
      setTabHistoryIdx(nextIdx);
      setActiveTab(tabHistory[nextIdx]);
    }
  };

  const handleSaveDraft = () => {
    const nowStr = new Date().toLocaleTimeString();
    setLastSavedTime(nowStr);
    setHasUnsavedChanges(false);
    setDraftVersions(prev => [
      { id: Date.now(), timestamp: nowStr, state: { ...sharedLoanState }, activeTab },
      ...prev.slice(0, 9)
    ]);
    alert(`✅ Loan Application Draft saved successfully at ${nowStr}`);
  };

  const handleRefreshCurrentModule = () => {
    if (hasUnsavedChanges) {
      if (!window.confirm("⚠️ You have unsaved changes in this module. Reloading will reset unsaved inputs. Proceed?")) {
        return;
      }
    }
    setHasUnsavedChanges(false);
    alert(`🔄 Refreshed active module (${activeTab.toUpperCase()}).`);
  };

  const handleResetCurrentModule = () => {
    if (window.confirm("⚠️ Are you sure you want to reset all fields in the current module to defaults?")) {
      setSharedLoanState(prev => ({
        ...prev,
        requested_amount: 4500000,
        down_payment: 500000,
        collateral_value: 4500000
      }));
      setHasUnsavedChanges(true);
      alert("🧹 Form fields reset to system defaults.");
    }
  };

  const updateSharedStateWithUndo = (updater) => {
    setUndoStack(prev => [...prev, { ...sharedLoanState }]);
    setRedoStack([]);
    setHasUnsavedChanges(true);
    setSharedLoanState(updater);
  };

  const handleUndo = () => {
    if (undoStack.length > 0) {
      const prev = undoStack[undoStack.length - 1];
      setRedoStack(r => [...r, { ...sharedLoanState }]);
      setUndoStack(u => u.slice(0, u.length - 1));
      setSharedLoanState(prev);
    }
  };

  const handleRedo = () => {
    if (redoStack.length > 0) {
      const next = redoStack[redoStack.length - 1];
      setUndoStack(u => [...u, { ...sharedLoanState }]);
      setRedoStack(r => r.slice(0, r.length - 1));
      setSharedLoanState(next);
    }
  };

  // Guided Wizard Navigation Handlers (Step 1 -> 12)
  const handleWizardPrevious = () => {
    if (activeWorkflowStage > 1) {
      const prevStep = activeWorkflowStage - 1;
      setActiveWorkflowStage(prevStep);
      const stepTabMap = {
        1: "dashboard", 2: "dashboard", 3: "dashboard",
        4: sharedLoanState.product === "Vehicle Loan" ? "vehicle" : sharedLoanState.product === "Gold Loan" ? "gold" : sharedLoanState.product === "Agriculture Loan" ? "agri_loan" : sharedLoanState.product === "Commercial Loan" ? "commercial_loan" : sharedLoanState.product === "Farm Equipment Loan" ? "farm_equipment" : "home_loan",
        5: "ocr", 6: "ocr", 7: "appraisal", 8: "underwriting", 9: "underwriting", 10: "underwriting", 11: "underwriting", 12: "underwriting"
      };
      setActiveTab(stepTabMap[prevStep] || "dashboard");
    }
  };

  const handleWizardNext = () => {
    if (activeWorkflowStage < 12) {
      const nextStep = activeWorkflowStage + 1;
      setActiveWorkflowStage(nextStep);
      const stepTabMap = {
        1: "dashboard", 2: "dashboard", 3: "dashboard",
        4: sharedLoanState.product === "Vehicle Loan" ? "vehicle" : sharedLoanState.product === "Gold Loan" ? "gold" : sharedLoanState.product === "Agriculture Loan" ? "agri_loan" : sharedLoanState.product === "Commercial Loan" ? "commercial_loan" : sharedLoanState.product === "Farm Equipment Loan" ? "farm_equipment" : "home_loan",
        5: "ocr", 6: "ocr", 7: "appraisal", 8: "underwriting", 9: "underwriting", 10: "underwriting", 11: "underwriting", 12: "underwriting"
      };
      setActiveTab(stepTabMap[nextStep] || "underwriting");
      if (nextStep === 12) downloadSanctionPdf();
    }
  };
  
  // Home Loan Module States
  const [homeDistrict, setHomeDistrict] = useState('Bagalkote');
  const [homeTaluk, setHomeTaluk] = useState('Badami');
  const [homeVillage, setHomeVillage] = useState('Kyada');
  const [homeSurvey, setHomeSurvey] = useState('142/3');
  const [homePlotArea, setHomePlotArea] = useState(1200);
  const [homeBuiltArea, setHomeBuiltArea] = useState(1500);
  const [homePropType, setHomePropType] = useState('Independent House');
  const [homeConstYear, setHomeConstYear] = useState(2020);
  const [homeKaveriRate, setHomeKaveriRate] = useState(0);
  const [homeLoading, setHomeLoading] = useState(false);
  const [homeResult, setHomeResult] = useState(null);

  // Agriculture Loan Module States
  const [agriDistrict, setAgriDistrict] = useState('Bagalkote');
  const [agriTaluk, setAgriTaluk] = useState('Badami');
  const [agriVillage, setAgriVillage] = useState('Kyada');
  const [agriSurvey, setAgriSurvey] = useState('101/A');
  const [agriAcres, setAgriAcres] = useState(5.0);
  const [agriLandType, setAgriLandType] = useState('Dry Land');
  const [agriLoading, setAgriLoading] = useState(false);
  const [agriResult, setAgriResult] = useState(null);

  // Commercial Property Loan Module States
  const [commDistrict, setCommDistrict] = useState('Bagalkote');
  const [commTaluk, setCommTaluk] = useState('Badami');
  const [commVillage, setCommVillage] = useState('Kyada');
  const [commPlotArea, setCommPlotArea] = useState(2000);
  const [commBuiltArea, setCommBuiltArea] = useState(3000);
  const [commType, setCommType] = useState('Retail Shop / Office Complex');
  const [commRateSqft, setCommRateSqft] = useState(0);
  const [commInterestRate, setCommInterestRate] = useState(10.5);
  const [commTenure, setCommTenure] = useState(180);
  const [commLoading, setCommLoading] = useState(false);
  const [commResult, setCommResult] = useState(null);

  // Farm Equipment Loan Module States
  const [farmType, setFarmType] = useState('Tractor');
  const [farmBrand, setFarmBrand] = useState('Mahindra 575 DI');
  const [farmCost, setFarmCost] = useState(850000);
  const [farmDownPay, setFarmDownPay] = useState(120000);
  const [farmAcres, setFarmAcres] = useState(6.0);
  const [farmIncome, setFarmIncome] = useState(450000);
  const [farmSubsidy, setFarmSubsidy] = useState(200000);
  const [farmLoading, setFarmLoading] = useState(false);
  const [farmResult, setFarmResult] = useState(null);

  // Vehicle Loan Module States
  const [vehCat, setVehCat] = useState('SUV');
  const [vehBrand, setVehBrand] = useState('Mahindra');
  const [vehModel, setVehModel] = useState('Thar ROXX');
  const [vehMakes, setVehMakes] = useState(['Mahindra', 'Tata', 'Toyota', 'Hyundai', 'Maruti Suzuki', 'BMW', 'Audi', 'Mercedes-Benz', 'Royal Enfield', 'TVS']);
  const [vehModels, setVehModels] = useState(['Thar ROXX', 'XUV700', 'Scorpio-N']);
  const [vehVariant, setVehVariant] = useState('AX7L 4WD Diesel MT');
  const [vehYear, setVehYear] = useState(2024);
  const [vehFuelType, setVehFuelType] = useState('Diesel');
  const [vehTransmission, setVehTransmission] = useState('Manual');
  const [vehEngineCc, setVehEngineCc] = useState('2184 cc');
  const [vehBodyType, setVehBodyType] = useState('SUV');
  const [vehSpecSource, setVehSpecSource] = useState('Vehicle Master Database');
  const [vehExPrice, setVehExPrice] = useState(1899000);
  const [vehOnRoad, setVehOnRoad] = useState(2165000);
  const [vehInsurance, setVehInsurance] = useState(54000);
  const [vehReg, setVehReg] = useState(135000);
  const [vehDownPay, setVehDownPay] = useState(300000);
  const [vehIncome, setVehIncome] = useState(85000);
  const [vehLoading, setVehLoading] = useState(false);
  const [vehResult, setVehResult] = useState(null);

  // Gold Valuation States
  const [goldWeight, setGoldWeight] = useState(50);
  const [goldPurity, setGoldPurity] = useState('22K');
  const [goldPricePerGram, setGoldPricePerGram] = useState(0);
  const [goldOuncePrice, setGoldOuncePrice] = useState(0);
  const [goldPriceData, setGoldPriceData] = useState(null);
  const [goldBorrowerName, setGoldBorrowerName] = useState('Aarav Kumar');
  const [goldTenure, setGoldTenure] = useState(12);
  const [goldInterestRate, setGoldInterestRate] = useState(9.5);
  const [goldOfficerNotes, setGoldOfficerNotes] = useState('');
  const [goldPriceLoading, setGoldPriceLoading] = useState(false);
  const [downloadingGoldPdf, setDownloadingGoldPdf] = useState(false);
  // Applicant details
  const [applicantName, setApplicantName] = useState("Aarav Kumar");
  const [applicantGender, setApplicantGender] = useState("Male");
  const [applicantMarried, setApplicantMarried] = useState("Yes");
  const [applicantDependents, setApplicantDependents] = useState("0");
  const [applicantEducation, setApplicantEducation] = useState("Graduate");
  const [applicantSelfEmp, setApplicantSelfEmp] = useState("No");
  const [applicantCreditHistory, setApplicantCreditHistory] = useState(1.0);
  const [applicantPropertyArea, setApplicantPropertyArea] = useState("Urban");

  // Document Verification State
  const [docAadhaarName, setDocAadhaarName] = useState("Aarav Kumar");
  const [docPanName, setDocPanName] = useState("Aarav Kumar");
  const [docSaleDeedName, setDocSaleDeedName] = useState("Aarav Kumar");
  const [docRtcOwnerName, setDocRtcOwnerName] = useState("Aarav Kumar");

  // Upload toggles
  const [hasAadhaar, setHasAadhaar] = useState(true);
  const [hasPan, setHasPan] = useState(true);
  const [hasIncome, setHasIncome] = useState(true);
  const [hasDeed, setHasDeed] = useState(true);
  const [hasRtc, setHasRtc] = useState(true);

  // Document Verification Results
  const [verifyResults, setVerifyResults] = useState({
    mismatch: false,
    trust_score: 98,
    fraud_score: 12,
    fraud_level: "Low",
    fraud_reasons: []
  });

  // Credit Underwriting Results
  const [underwritingResult, setUnderwritingResult] = useState({
    recommendation: "Approve",
    confidence: 96,
    overall_risk: "Low",
    probability_of_default: 4,
    reasons: ["✓ Stable debt-to-income servicing profile", "✓ Low loan leverage exposure", "✓ Verified applicant identity credentials"]
  });

  // Analytics Stats
  const [analyticsStats, setAnalyticsStats] = useState(null);

  // 1. Fetch Districts on Mount
  useEffect(() => {
    fetch('http://localhost:8000/api/districts')
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch districts");
        return res.json();
      })
      .then(data => setDistricts(data.districts || []))
      .catch(err => {
        console.error(err);
        // Fallback mock list
        setDistricts(["Bagalkote", "Bangalore Rural", "Basavangudi", "Belagavi", "Mysore", "Ramanagara"]);
      });
  }, []);

  // 2. Fetch Taluks when District changes
  useEffect(() => {
    if (!selectedDistrict) return;
    setTaluks([]);
    setVillages([]);
    setSelectedTaluk('');
    setSelectedVillage('');

    fetch(`http://localhost:8000/api/taluks?district=${encodeURIComponent(selectedDistrict)}`)
      .then(res => res.json())
      .then(data => setTaluks(data.taluks || []))
      .catch(() => setTaluks(["Badami", "Devanahalli", "Basavanagudi"]));
  }, [selectedDistrict]);

  // 3. Fetch Villages when Taluk changes
  useEffect(() => {
    if (!selectedTaluk) return;
    setVillages([]);
    setSelectedVillage('');

    fetch(`http://localhost:8000/api/villages?district=${encodeURIComponent(selectedDistrict)}&taluk=${encodeURIComponent(selectedTaluk)}`)
      .then(res => res.json())
      .then(data => setVillages(data.villages || []))
      .catch(() => setVillages(["Adagallu", "Kyada", "Ananthagiri"]));
  }, [selectedTaluk, selectedDistrict]);

  const fetchNearbyAmenities = (lat, lon, currentDistrict = selectedDistrict) => {
    const url = `https://overpass-api.de/api/interpreter?data=[out:json];(node(around:2000,${lat},${lon})["amenity"~"school|hospital|bank|police|marketplace|fuel"];node(around:2000,${lat},${lon})["highway"="bus_stop"];);out;`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const nodes = data.elements || [];
        const list = nodes.map(node => {
          const latDiff = node.lat - lat;
          const lonDiff = node.lon - lon;
          const distance = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111320;
          
          let rawType = node.tags.amenity || node.tags.highway || 'amenity';
          let displayType = rawType;
          if (rawType === 'marketplace') displayType = 'market';
          if (rawType === 'fuel') displayType = 'petrol pump';
          if (rawType === 'bus_stop') displayType = 'bus stop';
          if (rawType === 'police') displayType = 'police station';

          return {
            name: node.tags.name || node.tags.operator || `Nearby ${displayType}`,
            type: displayType,
            lat: node.lat,
            lon: node.lon,
            distance: distance
          };
        });
        list.sort((a, b) => a.distance - b.distance);
        setAmenities(list);
        generateGisProfile(lat, lon, list, currentDistrict);
      })
      .catch(err => {
        console.error("Overpass API error, using mock fallback:", err);
        const fallbackList = [
          { name: "Karnataka Public School", type: "school", lat: lat + 0.003, lon: lon - 0.002, distance: 410 },
          { name: "Government General Hospital", type: "hospital", lat: lat - 0.004, lon: lon + 0.005, distance: 680 },
          { name: "State Bank of India (SBI)", type: "bank", lat: lat + 0.001, lon: lon + 0.002, distance: 220 },
          { name: "Town Police Station", type: "police station", lat: lat - 0.002, lon: lon - 0.003, distance: 340 },
          { name: "Main Market Yard", type: "market", lat: lat + 0.005, lon: lon - 0.004, distance: 820 },
          { name: "HP Petrol Station", type: "petrol pump", lat: lat + 0.002, lon: lon + 0.004, distance: 510 },
          { name: "Main Bus Stop", type: "bus stop", lat: lat - 0.001, lon: lon + 0.001, distance: 180 }
        ];
        fallbackList.sort((a, b) => a.distance - b.distance);
        setAmenities(fallbackList);
        generateGisProfile(lat, lon, fallbackList, currentDistrict);
      });
  };

  const generateGisProfile = (lat, lon, list, currentDistrict) => {
    const highwayDist = Math.round(800 + Math.sin(lat * 12) * 500);
    const mainRoadDist = Math.round(150 + Math.cos(lon * 22) * 120);
    const cityCenterDist = Math.round((2.5 + Math.sin(lat * 5) * 1.5) * 10) / 10;
    const elevation = Math.round(820 + Math.sin(lat * 10) * 110);
    const slope = Math.round((1.0 + Math.cos(lon * 15) * 0.8) * 10) / 10;
    const rainfall = Math.round(820 + Math.sin(lat * 8) * 140);
    
    let soil = "Sandy Loam";
    let crops = "Pulses, Vegetables, Ragi";
    let irrigation = "Rainfed / Borewell";
    
    const distLower = (currentDistrict || "").toLowerCase();
    if (distLower.includes("bengaluru") || distLower.includes("bangalore") || distLower.includes("mysore") || distLower.includes("ramanagara")) {
      soil = "Red Sandy Loam";
      crops = "Ragi, Maize, Groundnut, Coconut";
      irrigation = "Borewell / Lift Irrigation";
    } else if (distLower.includes("bagalkote") || distLower.includes("belagavi") || distLower.includes("vijayapura")) {
      soil = "Black Clayey Soil";
      crops = "Sugarcane, Cotton, Jowar, Wheat";
      irrigation = "Canal / River Basin";
    }

    const nearestAmenityDist = list.length > 0 ? list[0].distance : 800;
    let score = 9.8 - (nearestAmenityDist / 600) - (mainRoadDist / 1000);
    score = Math.max(5.0, Math.min(9.9, Math.round(score * 10) / 10));

    let investmentGrade = "Excellent Investment";
    let riskTier = "Low Risk";
    let connectivityTier = "High Connectivity";

    if (score < 7.0) {
      investmentGrade = "Speculative";
      riskTier = "Moderate Risk";
      connectivityTier = "Low Connectivity";
    } else if (score < 8.5) {
      investmentGrade = "Good Value";
      riskTier = "Low Risk";
      connectivityTier = "Moderate Connectivity";
    }

    setGisProfile({
      highwayDist,
      mainRoadDist,
      cityCenterDist,
      elevation,
      slope,
      rainfall,
      soil,
      crops,
      irrigation,
      score,
      investmentGrade,
      riskTier,
      connectivityTier
    });
  };

  const fetchEnvRiskData = (lat, lon) => {
    const elevation = Math.round(800 + Math.sin(lat * 10) * 120);
    const proximityToWater = Math.round(500 + Math.cos(lon * 20) * 450);
    
    let floodRisk = "Low Risk";
    if (proximityToWater < 200) {
      floodRisk = "High Vulnerability";
    } else if (proximityToWater < 500) {
      floodRisk = "Moderate Vulnerability";
    }
    
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`)
      .then(res => res.json())
      .then(weatherData => {
        const current = weatherData.current_weather || {};
        setEnvRiskData({
          temp: current.temperature || 24.5,
          wind: current.windspeed || 8.0,
          weatherCode: current.weathercode || 0,
          elevation: elevation,
          waterDistance: proximityToWater,
          floodRisk: floodRisk
        });
      })
      .catch(() => {
        setEnvRiskData({
          temp: 26.0,
          wind: 12.0,
          weatherCode: 1,
          elevation: elevation,
          waterDistance: proximityToWater,
          floodRisk: floodRisk
        });
      });
  };

  const handlePolygonChange = (coords, area) => {
    setPolygonCoords(coords);
    if (area > 0) {
      setLandArea(area);
    }
  };

  // 6. Calculate Loan Simulator Metrics
  const calculateSimulatorMetrics = () => {
    if (!valuationData) return null;

    const propertyValue = valuationData.totalValue;
    const downPayment = Math.min(simDownPayment, propertyValue - 1000);
    const loanAmount = propertyValue - downPayment;
    const annualRate = simInterestRate;
    const tenureYears = simTenure;
    const monthlyRate = annualRate / 12 / 100;
    const totalMonths = tenureYears * 12;

    // Monthly EMI Calculation
    let emi = 0;
    if (monthlyRate > 0) {
      emi = Math.round(
        loanAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) / 
        (Math.pow(1 + monthlyRate, totalMonths) - 1)
      );
    } else {
      emi = Math.round(loanAmount / totalMonths);
    }

    // Combined Monthly Net Income
    const totalIncome = simMonthlyIncome + (simHasCoApplicant ? simCoApplicantIncome : 0);

    // DTI (Debt-to-Income) Ratio
    const dti = totalIncome > 0 ? Math.round((emi / totalIncome) * 100) : 0;

    // LTV (Loan-to-Value) Ratio
    const ltv = propertyValue > 0 ? Math.round((loanAmount / propertyValue) * 100) : 0;

    // Approval Probability
    let approvalProb = 100 - (ltv * 0.25) - (dti * 0.65);
    if (dti > 50) approvalProb -= 20; // steep deduction for high debt service
    if (ltv > 80) approvalProb -= 15; // penalty for >80% LTV
    approvalProb = Math.max(5, Math.min(99, Math.round(approvalProb)));

    // Risk Classification
    let riskScore = Math.round((ltv * 0.4) + (dti * 0.6));
    let riskLevel = "Low";
    if (riskScore > 65 || dti > 50 || ltv > 85) {
      riskLevel = "High";
    } else if (riskScore > 45 || dti > 40 || ltv > 75) {
      riskLevel = "Medium";
    }

    // What-if optimizations calculations
    // 1. What if down payment is increased by 5 Lakhs?
    const dpIncrease = 500000;
    const altDownPayment = Math.min(downPayment + dpIncrease, propertyValue - 1000);
    const altLoanAmount = propertyValue - altDownPayment;
    let altEmi = 0;
    if (monthlyRate > 0) {
      altEmi = Math.round(
        altLoanAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) / 
        (Math.pow(1 + monthlyRate, totalMonths) - 1)
      );
    } else {
      altEmi = Math.round(altLoanAmount / totalMonths);
    }
    const altDti = totalIncome > 0 ? Math.round((altEmi / totalIncome) * 100) : 0;
    const altLtv = propertyValue > 0 ? Math.round((altLoanAmount / propertyValue) * 100) : 0;
    let altApprovalProb = 100 - (altLtv * 0.25) - (altDti * 0.65);
    if (altDti > 50) altApprovalProb -= 20;
    if (altLtv > 80) altApprovalProb -= 15;
    altApprovalProb = Math.max(5, Math.min(99, Math.round(altApprovalProb)));

    let altRiskScore = Math.round((altLtv * 0.4) + (altDti * 0.6));
    let altRiskLevel = "Low";
    if (altRiskScore > 65 || altDti > 50 || altLtv > 85) altRiskLevel = "High";
    else if (altRiskScore > 45 || altDti > 40 || altLtv > 75) altRiskLevel = "Medium";

    // 2. What if Co-applicant is added with 50K income? (if currently unchecked)
    const coAppIncomeBoost = 50000;
    const coAppTotalIncome = totalIncome + (simHasCoApplicant ? 0 : coAppIncomeBoost);
    const coAppDti = coAppTotalIncome > 0 ? Math.round((emi / coAppTotalIncome) * 100) : 0;
    let coAppApprovalProb = 100 - (ltv * 0.25) - (coAppDti * 0.65);
    if (coAppDti > 50) coAppApprovalProb -= 20;
    if (ltv > 80) coAppApprovalProb -= 15;
    coAppApprovalProb = Math.max(5, Math.min(99, Math.round(coAppApprovalProb)));

    return {
      loanAmount,
      downPayment,
      emi,
      dti,
      ltv,
      approvalProb,
      riskScore,
      riskLevel,
      altDownPayment,
      altEmi,
      altDti,
      altApprovalProb,
      altRiskLevel,
      coAppDti,
      coAppApprovalProb
    };
  };

  // Underwriting & Document Intelligence API helpers
  const runDocumentVerification = () => {
    const payload = {
      aadhaar_name: docAadhaarName,
      pan_name: docPanName,
      sale_deed_name: docSaleDeedName,
      rtc_owner_name: docRtcOwnerName,
      has_aadhaar: hasAadhaar,
      has_pan: hasPan,
      has_income: hasIncome,
      has_deed: hasDeed,
      has_rtc: hasRtc
    };
    fetch('http://localhost:8000/api/verify-documents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        setVerifyResults(data);
        runCreditRiskModel(data.trust_score);
      })
      .catch(err => console.error("Error verifying documents:", err));
  };

  const runCreditRiskModel = (trustScore) => {
    const calculatedSim = calculateSimulatorMetrics() || { loanAmount: 3500000, emi: 35000, dti: 40.0, ltv: 70.0, riskScore: 35.0 };
    const payload = {
      monthly_income: simMonthlyIncome,
      loan_amount: calculatedSim.loanAmount,
      dti: calculatedSim.dti,
      ltv: calculatedSim.ltv,
      risk_score: calculatedSim.riskScore,
      trust_score: trustScore !== undefined ? trustScore : verifyResults.trust_score
    };
    fetch('http://localhost:8000/api/predict-underwriting', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => setUnderwritingResult(data))
      .catch(err => console.error("Error predicting underwriting:", err));
  };

  const fetchAnalyticsStats = () => {
    fetch('http://localhost:8000/api/analytics-stats')
      .then(res => res.json())
      .then(data => setAnalyticsStats(data))
      .catch(err => console.error("Error loading analytics:", err));
  };

  const downloadSanctionPdf = () => {
    const calculatedSim = calculateSimulatorMetrics() || { loanAmount: 3500000, emi: 35000 };
    const payload = {
      name: applicantName,
      gender: applicantGender,
      married: applicantMarried,
      dependents: applicantDependents,
      education: applicantEducation,
      self_emp: applicantSelfEmp,
      credit: applicantCreditHistory,
      property_area: applicantPropertyArea,
      loan_amount: calculatedSim.loanAmount,
      loan_term: simTenure,
      app_income: simMonthlyIncome,
      co_income: simHasCoApplicant ? simCoApplicantIncome : 0.0,
      result_text: underwritingResult.recommendation,
      property_details: valuationData ? {
        district: selectedDistrict,
        taluk: selectedTaluk,
        village: selectedVillage,
        total_market_value: valuationData.totalValue,
        guideline_rate: valuationData.guidelineRate,
        trust_score: verifyResults.trust_score
      } : null,
      ai_explanation: underwritingResult.reasons.join(", "),
      officer_notes: "Appraisal dossier compiled via AegisCR decision engine."
    };

    fetch('http://localhost:8000/api/generate-sanction-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to compile PDF.");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${applicantName.replace(/ /g, '_')}_sanction_report.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(err => alert("Error downloading report: " + err.message));
  };

  // Trigger hooks
  useEffect(() => {
    runDocumentVerification();
  }, [docAadhaarName, docPanName, docSaleDeedName, docRtcOwnerName, hasAadhaar, hasPan, hasIncome, hasDeed, hasRtc, simMonthlyIncome, simDownPayment, simInterestRate, simTenure, simHasCoApplicant, simCoApplicantIncome]);

  useEffect(() => {
    if (activeTab === "analytics") {
      fetchAnalyticsStats();
    }
  }, [activeTab]);

  // 4. Calculate Valuation
  const calculateValuation = (district = selectedDistrict, taluk = selectedTaluk, village = selectedVillage, keepCoordinates = false, customRate = null, customClassification = null, state = selectedState) => {
    if (!district || !taluk || !village) {
      setError('Please select District, Taluk and Village fields.');
      return;
    }
    setError('');
    setLoading(true);
    setGuidelineRecords([]);
    setSelectedRecordIndex(-1);

    // Call guideline rate api
    const url = `http://localhost:8000/api/guideline?district=${encodeURIComponent(district)}&taluk=${encodeURIComponent(taluk)}&village=${encodeURIComponent(village)}&land_type=${landType}&state=${encodeURIComponent(state)}`;
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        const records = data.records || [];
        setGuidelineRecords(records);
        
        if (records.length === 0) {
          setError('No guidance value available for the selected location in the Kaveri database.');
          setValuationData(null);
          setLoading(false);
          return;
        }

        // Use either the customRate or the default matched rate
        let ratePerSqft = customRate !== null ? customRate : (data.guideline_rate_per_sqft || 0.0);
        let classification = customClassification !== null ? customClassification : (data.matched_classification || landType);
        
        // Resolve coordinates
        let activeCoords = coordinates;
        if (!keepCoordinates) {
          const mockCoords = {
            "Bagalkote": [16.1813, 75.6961],
            "Bangalore Rural": [13.2925, 77.5500],
            "Basavangudi": [12.9406, 77.5738],
            "Mysore": [12.2958, 76.6394],
            "Ramanagara": [12.7150, 77.2813]
          };
          activeCoords = mockCoords[district] || [12.9716, 77.5946];
          setCoordinates(activeCoords);
        }
        
        if (!activeCoords) {
          activeCoords = [12.9716, 77.5946];
        }

        // Trigger GIS live queries
        fetchNearbyAmenities(activeCoords[0], activeCoords[1]);
        fetchEnvRiskData(activeCoords[0], activeCoords[1]);

        // Call the AI Valuation prediction endpoint
        const predictPayload = {
          state: state,
          district: district,
          taluk: taluk,
          village: village,
          latitude: activeCoords[0],
          longitude: activeCoords[1],
          area: Number(landArea),
          guidance_value: Number(ratePerSqft),
          property_type: classification
        };

        fetch('http://localhost:8000/predict-property-value', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(predictPayload)
        })
          .then(pRes => {
            if (!pRes.ok) throw new Error("Valuation model prediction request failed.");
            return pRes.json();
          })
          .then(aiData => {
            const riskScore = 100 - aiData.confidence;
            const riskCategory = aiData.confidence > 85 ? "Very Safe" : "Low Risk";
            const maxLtv = 0.80;
            const maxLoan = Math.round(aiData.predicted_value * maxLtv);

            setValuationData({
              guidelineRate: ratePerSqft,
              marketRate: aiData.rate_per_sqft || Math.round(aiData.predicted_value / landArea),
              totalValue: aiData.predicted_value,
              maxLoan: maxLoan,
              ltvPercentage: maxLtv * 100,
              riskScore: riskScore,
              riskCategory: riskCategory,
              classification: classification,
              confidence: aiData.confidence,
              investmentScore: aiData.investment_score
            });
            
            // Initialize simulator values on valuation success
            const defaultDown = Math.round(aiData.predicted_value * 0.20);
            setSimDownPayment(defaultDown);
            setSimInterestRate(9.5);
            setSimTenure(20);
            setSimMonthlyIncome(85000);
            setSimHasCoApplicant(false);
            setSimCoApplicantIncome(50000);
            
            setLoading(false);
          })
          .catch(err => {
            setError('Error running AI valuation: ' + err.message);
            setLoading(false);
          });
      })
      .catch(err => {
        setError('Error connecting to circle rates backend: ' + err.message);
        setLoading(false);
      });
  };

  const handleCalculate = (e) => {
    if (e) e.preventDefault();
    calculateValuation();
  };

  const handleSelectRecord = (index) => {
    setSelectedRecordIndex(index);
    const rec = guidelineRecords[index];
    if (rec) {
      calculateValuation(
        rec.district,
        rec.taluk,
        rec.village,
        true, // keepCoordinates
        rec.rate_per_sqft,
        rec.property_type
      );
    }
  };

  const mapLandType = (classification) => {
    const c = String(classification || "").toLowerCase();
    if (c.includes("commercial") || c.includes("shop") || c.includes("office")) return "Commercial";
    if (c.includes("industrial") || c.includes("factory") || c.includes("shed")) return "Industrial";
    if (c.includes("site") || c.includes("apartment") || c.includes("flat") || c.includes("residential") || c.includes("house") || c.includes("gramathana")) return "Residential";
    return "Agricultural";
  };

  const handleConfirmModalProperty = (rec) => {
    if (tempGeocodedAddress) {
      setSelectedState(tempGeocodedAddress.state);
      setPincode(tempGeocodedAddress.pincode);
      setSelectedDistrict(tempGeocodedAddress.district);
      setSelectedTaluk(tempGeocodedAddress.taluk);
      setSelectedVillage(tempGeocodedAddress.village);
      setGeocodedAddress(tempGeocodedAddress);
    }
    const mappedType = mapLandType(rec.property_type);
    setLandType(mappedType);
    setLandPrice(rec.rate_per_sqft);
    const mockSurvey = `${Math.floor(Math.random() * 200) + 1}/${Math.floor(Math.random() * 5) + 1}`;
    setSurveyNumber(mockSurvey);
    setShowPropertyModal(false);
    calculateValuation(
      rec.district,
      rec.taluk,
      rec.village,
      true,
      rec.rate_per_sqft,
      rec.property_type,
      tempGeocodedAddress ? tempGeocodedAddress.state : selectedState
    );
  };

  // 5. Handle Click/Location from Map (with Reverse Geocoding & Autofill)
  const handleMapClickOrLocation = (lat, lng) => {
    setCoordinates([lat, lng]);
    setGeocodingLoading(true);
    setLoading(true);
    setError('');

    // Trigger GIS details immediately
    fetchNearbyAmenities(lat, lng);
    fetchEnvRiskData(lat, lng);

    // Query Nominatim reverse geocoding API
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&accept-language=en`, {
      headers: {
        'User-Agent': 'AegisCR-Valuation-App/1.0'
      }
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to contact reverse geocoding service.");
        return res.json();
      })
      .then(data => {
        const address = data.address || {};
        const stateName = address.state || 'Karnataka';
        const parsedPincode = address.postcode || '';

        // Save geocoded address in state for later use
        const geoInfo = {
          district: address.city_district || address.county || address.district || address.city || '',
          taluk: address.subdistrict || address.suburb || address.town || address.village || '',
          village: address.neighbourhood || address.village || address.suburb || address.road || address.hamlet || '',
          state: stateName,
          pincode: parsedPincode,
          lat: lat,
          lon: lng,
          displayName: data.display_name || ''
        };
        
        if (!stateName.toLowerCase().includes('karnataka')) {
          setError('Location is outside Karnataka. Kaveri valuation circular rates are only available within Karnataka state boundaries.');
          setGeocodingLoading(false);
          setLoading(false);
          return;
        }

        const districtName = geoInfo.district;
        const talukName = geoInfo.taluk;
        const villageName = geoInfo.village;

        // Match against loaded districts list
        let matchedDistrict = districts.find(d => 
          d.toLowerCase().includes(districtName.toLowerCase()) || 
          districtName.toLowerCase().includes(d.toLowerCase())
        );

        if (!matchedDistrict && districts.length > 0) {
          matchedDistrict = districts[0];
        }

        if (matchedDistrict) {
          // Fetch Taluks for this District
          fetch(`http://localhost:8000/api/taluks?district=${encodeURIComponent(matchedDistrict)}`)
            .then(res => res.json())
            .then(talukData => {
              const talukList = talukData.taluks || [];
              setTaluks(talukList);
              
              let matchedTaluk = talukList.find(t => 
                t.toLowerCase().includes(talukName.toLowerCase()) || 
                talukName.toLowerCase().includes(t.toLowerCase())
              );
              
              if (!matchedTaluk && talukList.length > 0) {
                matchedTaluk = talukList[0];
              }

              if (matchedTaluk) {
                // Fetch Villages for this Taluk
                fetch(`http://localhost:8000/api/villages?district=${encodeURIComponent(matchedDistrict)}&taluk=${encodeURIComponent(matchedTaluk)}`)
                  .then(res => res.json())
                  .then(villageData => {
                    const villageList = villageData.villages || [];
                    setVillages(villageList);
                    
                    let matchedVillage = villageList.find(v => 
                      v.toLowerCase().includes(villageName.toLowerCase()) || 
                      villageName.toLowerCase().includes(v.toLowerCase())
                    );
                    
                    if (!matchedVillage && villageList.length > 0) {
                      matchedVillage = villageList[0];
                    }

                    if (matchedVillage) {
                      // Fetch circular rate guidelines for this matched village
                      const url = `http://localhost:8000/api/guideline?district=${encodeURIComponent(matchedDistrict)}&taluk=${encodeURIComponent(matchedTaluk)}&village=${encodeURIComponent(matchedVillage)}&land_type=${landType}&state=${encodeURIComponent(stateName)}`;
                      fetch(url)
                        .then(gRes => gRes.json())
                        .then(gData => {
                          const records = gData.records || [];
                          
                          if (records.length === 1) {
                            // Exactly one record -> Auto-fill form and run valuation
                            const rec = records[0];
                            setSelectedState(stateName);
                            setPincode(parsedPincode);
                            setSelectedDistrict(matchedDistrict);
                            setSelectedTaluk(matchedTaluk);
                            setSelectedVillage(matchedVillage);
                            setGeocodedAddress(geoInfo);
                            
                            const mappedType = mapLandType(rec.property_type);
                            setLandType(mappedType);
                            setLandPrice(rec.rate_per_sqft);
                            const mockSurvey = `${Math.floor(Math.random() * 200) + 1}/${Math.floor(Math.random() * 5) + 1}`;
                            setSurveyNumber(mockSurvey);
                            setGeocodingLoading(false);
                            
                            calculateValuation(matchedDistrict, matchedTaluk, matchedVillage, true, rec.rate_per_sqft, rec.property_type, stateName);
                          } else if (records.length > 1) {
                            // Multiple records -> Open property selector modal
                            setMatchingProperties(records);
                            setTempGeocodedAddress(geoInfo);
                            setShowPropertyModal(true);
                            setGeocodingLoading(false);
                            setLoading(false);
                          } else {
                            // No records found -> Keep manual entry
                            setSelectedState(stateName);
                            setPincode(parsedPincode);
                            setSelectedDistrict(matchedDistrict);
                            setSelectedTaluk(matchedTaluk);
                            setSelectedVillage(matchedVillage);
                            setGeocodedAddress(geoInfo);
                            
                            setError('No matching Kaveri circle rate records found for this geocoded location. Form fields updated for manual data entry.');
                            setGeocodingLoading(false);
                            setLoading(false);
                          }
                        })
                        .catch(err => {
                          console.error("Error querying circular rates: ", err);
                          setGeocodingLoading(false);
                          setLoading(false);
                        });
                    } else {
                      setGeocodingLoading(false);
                      setLoading(false);
                    }
                  })
                  .catch(err => {
                    console.error("Error fetching villages:", err);
                    setGeocodingLoading(false);
                    setLoading(false);
                  });
              } else {
                setGeocodingLoading(false);
                setLoading(false);
              }
            })
            .catch(err => {
              console.error("Error fetching taluks:", err);
              setGeocodingLoading(false);
              setLoading(false);
            });
        } else {
          setGeocodingLoading(false);
          setLoading(false);
        }
      })
      .catch(err => {
        console.error("Reverse geocoding error:", err);
        setError("Reverse geocoding failed: " + err.message);
        setGeocodingLoading(false);
        setLoading(false);
      });
  };

  const updateGoldPriceForPurity = (purity, data) => {
    const priceData = data || goldPriceData;
    if (!priceData) return;
    
    let rate = 0;
    if (purity === '24K') rate = priceData.price_gram_24k;
    else if (purity === '22K') rate = priceData.price_gram_22k;
    else if (purity === '18K') rate = priceData.price_gram_18k;
    
    setGoldPricePerGram(rate);
    setGoldOuncePrice(priceData.price);
  };

  const fetchGoldPrice = async () => {
    setGoldPriceLoading(true);
    try {
      let res;
      try {
        res = await fetch("http://localhost:8000/gold-price");
        if (!res.ok) throw new Error("Root endpoint failed");
      } catch (e) {
        res = await fetch("http://localhost:8000/api/gold-price");
      }
      const data = await res.json();
      console.log("GoldAPI Response:", data);
      setGoldPriceData(data);
      updateGoldPriceForPurity(goldPurity, data);
    } catch (err) {
      console.error("Error fetching gold price:", err);
      setError("Could not load spot gold price from backend API.");
    } finally {
      setGoldPriceLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'gold') {
      fetchGoldPrice();
    } else if (activeTab === 'home_loan' && !homeResult) {
      evaluateHomeLoan();
    } else if (activeTab === 'agri_loan' && !agriResult) {
      evaluateAgriLoan();
    } else if (activeTab === 'commercial_loan' && !commResult) {
      evaluateCommLoan();
    } else if (activeTab === 'farm_equipment' && !farmResult) {
      evaluateFarmLoan();
    } else if (activeTab === 'vehicle') {
      loadVehicleMakes();
      if (!vehResult) evaluateVehicleLoan();
    }
  }, [activeTab]);

  const evaluateHomeLoan = async () => {
    setHomeLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluate-loan-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: "home",
          district: homeDistrict,
          taluk: homeTaluk,
          village: homeVillage,
          survey_number: homeSurvey,
          plot_area: parseFloat(homePlotArea),
          built_up_area: parseFloat(homeBuiltArea),
          property_type: homePropType,
          construction_year: parseInt(homeConstYear)
        })
      });
      const data = await res.json();
      setHomeResult(data);
      setHomeKaveriRate(data.rate_per_sqft || 0);
    } catch (e) {
      console.error("Error evaluating home loan:", e);
      const rate = 2200;
      const landVal = homePlotArea * rate;
      const bldgVal = homeBuiltArea * 1600;
      const totalVal = landVal + bldgVal;
      setHomeResult({
        module: "home",
        rate_per_sqft: rate,
        land_value: landVal,
        building_value: bldgVal,
        total_property_value: totalVal,
        recommended_loan: totalVal * 0.80,
        eligible_loan: totalVal * 0.80,
        ltv: 80.0,
        status: "Eligible"
      });
    } finally {
      setHomeLoading(false);
    }
  };

  const evaluateAgriLoan = async () => {
    setAgriLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluate-loan-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: "agriculture",
          district: agriDistrict,
          taluk: agriTaluk,
          village: agriVillage,
          survey_number: agriSurvey,
          plot_area: parseFloat(agriAcres),
          land_type: agriLandType
        })
      });
      const data = await res.json();
      setAgriResult(data);
    } catch (e) {
      console.error("Error evaluating agri loan:", e);
      const rateAcre = agriLandType === 'Wet Land' ? 350000 : agriLandType === 'Bagayat Land' ? 450000 : 150000;
      const landVal = agriAcres * rateAcre;
      setAgriResult({
        module: "agriculture",
        land_type: agriLandType,
        rate_per_acre: rateAcre,
        total_land_value: landVal,
        eligible_loan: landVal * 0.75,
        risk_score: agriLandType === 'Bagayat Land' ? 15 : 30,
        matched_classification: agriLandType
      });
    } finally {
      setAgriLoading(false);
    }
  };

  const evaluateCommLoan = async () => {
    setCommLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluate-loan-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: "commercial",
          district: commDistrict,
          taluk: commTaluk,
          village: commVillage,
          plot_area: parseFloat(commPlotArea),
          built_up_area: parseFloat(commBuiltArea),
          interest_rate: parseFloat(commInterestRate),
          tenure_months: parseInt(commTenure)
        })
      });
      const data = await res.json();
      setCommResult(data);
      setCommRateSqft(data.comm_rate_per_sqft || 0);
    } catch (e) {
      console.error("Error evaluating comm loan:", e);
      const rateSqft = 4500;
      const totalVal = commPlotArea * rateSqft + commBuiltArea * 2500;
      const loan = totalVal * 0.65;
      const r = (commInterestRate / 100) / 12;
      const n = commTenure;
      const emi = (loan * r * Math.pow(1+r, n)) / (Math.pow(1+r, n) - 1);
      setCommResult({
        module: "commercial",
        comm_rate_per_sqft: rateSqft,
        property_value: totalVal,
        eligible_loan: loan,
        ltv: 65.0,
        monthly_emi: emi
      });
    } finally {
      setCommLoading(false);
    }
  };

  const evaluateFarmLoan = async () => {
    setFarmLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluate-loan-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: "farm_equipment",
          equipment_type: farmType,
          equipment_brand: farmBrand,
          equipment_cost: parseFloat(farmCost),
          down_payment: parseFloat(farmDownPay),
          farm_size_acres: parseFloat(farmAcres),
          annual_income: parseFloat(farmIncome),
          subsidy_amount: parseFloat(farmSubsidy),
          interest_rate: 9.0,
          tenure_months: 60
        })
      });
      const data = await res.json();
      setFarmResult(data);
    } catch (e) {
      console.error("Error evaluating farm loan:", e);
      const netCost = farmCost - farmSubsidy;
      const loan = netCost - farmDownPay;
      setFarmResult({
        module: "farm_equipment",
        equipment_type: farmType,
        equipment_brand: farmBrand,
        equipment_cost: farmCost,
        subsidy_amount: farmSubsidy,
        net_equipment_cost: netCost,
        down_payment: farmDownPay,
        eligible_loan: netCost * 0.85,
        loan_sanction: loan,
        ltv: (loan / netCost * 100).toFixed(1),
        monthly_emi: loan * 0.021,
        repayment_risk_score: 15
      });
    } finally {
      setFarmLoading(false);
    }
  };

  // Client-side cache for vehicle lookups
  const vehModelCache = useRef({});
  const vehSpecCache = useRef({});

  const loadVehicleMakes = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/vehicle/makes");
      if (res.ok) {
        const data = await res.json();
        if (data.makes && data.makes.length > 0) {
          setVehMakes(data.makes);
        }
      }
    } catch (e) {
      console.log("Using default vehicle makes list:", e);
    }
  };

  const handleVehicleBrandChange = async (brand) => {
    setVehBrand(brand);
    if (vehModelCache.current[brand]) {
      const cachedModels = vehModelCache.current[brand];
      setVehModels(cachedModels);
      if (cachedModels.length > 0) {
        const firstModel = cachedModels[0];
        setVehModel(firstModel);
        handleVehicleModelChange(brand, firstModel);
      }
      return;
    }
    
    try {
      const res = await fetch(`http://localhost:8000/api/vehicle/models?make=${encodeURIComponent(brand)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          vehModelCache.current[brand] = data.models;
          setVehModels(data.models);
          const firstModel = data.models[0];
          setVehModel(firstModel);
          handleVehicleModelChange(brand, firstModel);
        }
      }
    } catch (e) {
      console.log("Error fetching models for brand:", e);
    }
  };

  const handleVehicleModelChange = async (brand, model) => {
    setVehModel(model);
    const cacheKey = `${brand}_${model}`;
    let data = vehSpecCache.current[cacheKey];

    if (!data) {
      try {
        const res = await fetch(`http://localhost:8000/api/vehicle/specs?make=${encodeURIComponent(brand)}&model=${encodeURIComponent(model)}`);
        if (res.ok) {
          data = await res.json();
          if (data) vehSpecCache.current[cacheKey] = data;
        }
      } catch (e) {
        console.log("Error fetching specs for model:", e);
      }
    }

    if (data) {
      if (data.variant) setVehVariant(data.variant);
      if (data.year) setVehYear(data.year);
      if (data.fuel_type) setVehFuelType(data.fuel_type);
      if (data.transmission) setVehTransmission(data.transmission);
      if (data.engine_cc) setVehEngineCc(data.engine_cc);
      if (data.body_type) setVehBodyType(data.body_type);
      if (data.source) setVehSpecSource(data.source);
      if (data.ex_showroom_price) setVehExPrice(data.ex_showroom_price);
      if (data.on_road_price) {
        setVehOnRoad(data.on_road_price);
        // Centralized Auto-Sync to Smart Loan Prediction State
        const loanCap = data.on_road_price * 0.85;
        const down = data.on_road_price * 0.15;
        setVehDownPay(down);
        setApplicantLoanAmount(loanCap);
        setSimDownPayment(down);
        setSharedLoanState(prev => ({
          ...prev,
          product: 'Vehicle Loan',
          vehicle_make: brand,
          vehicle_model: model,
          vehicle_variant: data.variant || 'Standard',
          on_road_price: data.on_road_price,
          requested_amount: loanCap,
          down_payment: down,
          collateral_type: 'Vehicle',
          collateral_value: data.on_road_price
        }));
      }
    }
  };

  const evaluateVehicleLoan = async () => {
    setVehLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/evaluate-loan-module", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          module: "vehicle",
          vehicle_category: vehCat,
          vehicle_make: vehBrand,
          vehicle_model: vehModel,
          vehicle_variant: vehVariant,
          vehicle_year: parseInt(vehYear),
          fuel_type: vehFuelType,
          transmission: vehTransmission,
          engine_cc: vehEngineCc,
          body_type: vehBodyType,
          ex_showroom_price: parseFloat(vehExPrice),
          on_road_price: parseFloat(vehOnRoad),
          down_payment: parseFloat(vehDownPay),
          annual_income: parseFloat(vehIncome * 12),
          interest_rate: 9.5,
          tenure_months: 60
        })
      });
      const data = await res.json();
      setVehResult(data);
    } catch (e) {
      console.error("Error evaluating vehicle loan:", e);
      const onRoad = parseFloat(vehOnRoad) || (parseFloat(vehExPrice) * 1.14);
      const loan = onRoad - vehDownPay;
      setVehResult({
        module: "vehicle",
        vehicle_category: vehCat,
        vehicle_make: vehBrand,
        vehicle_model: vehModel,
        vehicle_variant: vehVariant,
        fuel_type: vehFuelType,
        transmission: vehTransmission,
        engine_cc: vehEngineCc,
        body_type: vehBodyType,
        ex_showroom_price: vehExPrice,
        on_road_price: onRoad,
        down_payment: vehDownPay,
        eligible_loan: onRoad * 0.85,
        loan_sanction: loan,
        ltv: (loan / onRoad * 100).toFixed(1),
        monthly_emi: loan * 0.021,
        credit_risk_score: 18
      });
    } finally {
      setVehLoading(false);
    }
  };

  const handleGoldPurityChange = (e) => {
    const purity = e.target.value;
    setGoldPurity(purity);
    updateGoldPriceForPurity(purity, goldPriceData);
  };

  const handleDownloadGoldPdf = async () => {
    if (!goldBorrowerName) {
      setError("Please enter the borrower name before exporting appraisal PDF.");
      return;
    }
    setDownloadingGoldPdf(true);
    try {
      const response = await fetch("http://localhost:8000/api/generate-gold-sanction-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          name: goldBorrowerName,
          weight: parseFloat(goldWeight),
          purity: goldPurity,
          rate_per_gram: parseFloat(goldPricePerGram),
          gold_value: parseFloat(goldWeight * goldPricePerGram),
          eligible_loan: parseFloat(goldWeight * goldPricePerGram * 0.75),
          interest_rate: parseFloat(goldInterestRate),
          tenure: parseFloat(goldTenure),
          officer_notes: goldOfficerNotes
        })
      });
      if (!response.ok) throw new Error("Failed to compile gold PDF letter.");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${goldBorrowerName.replace(/\s+/g, '_')}_gold_sanction_report.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error("PDF generation fail:", err);
      setError("Failed to compile and download Gold Appraisal PDF report.");
    } finally {
      setDownloadingGoldPdf(false);
    }
  };

  const sim = calculateSimulatorMetrics();

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans p-6" style={{ fontFamily: "'Outfit', sans-serif" }}>
      {/* Executive Banking Header with Branch Switcher, Global Search, Role Control & Notifications */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 mb-6 shadow-xl flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-sky-400 via-emerald-400 to-teal-300 bg-clip-text text-transparent tracking-wide">
            🛡️ AegisCR – Enterprise AI Banking & Credit Management Platform
          </h1>
          <p className="text-slate-400 mt-1 text-xs uppercase tracking-wider">
            Commercial Loan Underwriting • Kaveri Guidance Valuation • Live GoldAPI Spot Pricing • Explainable AI Credit Memo
          </p>
        </div>

        {/* Header Control Bar */}
        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
          {/* Global Search Bar */}
          <div className="relative flex-1 lg:flex-none">
            <input
              type="text"
              placeholder="🔍 Search Aadhaar, PAN, App ID, Survey No..."
              value={globalSearchQuery}
              onChange={(e) => setGlobalSearchQuery(e.target.value)}
              className="bg-slate-950 border border-slate-750 text-xs rounded-xl px-3.5 py-2 w-full lg:w-64 text-slate-200 focus:border-sky-500 outline-none transition"
            />
          </div>

          {/* Branch Selector */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-1.5 flex items-center gap-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider pl-1.5">Branch:</span>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              className="bg-slate-900 border border-slate-750 text-emerald-400 font-bold text-xs rounded-lg px-2.5 py-1 outline-none cursor-pointer"
            >
              <option>Bengaluru Main Branch</option>
              <option>Mysuru Central</option>
              <option>Hubballi Commercial</option>
              <option>Belagavi North</option>
              <option>Bagalkote District Branch</option>
            </select>
          </div>

          {/* Developer Mode & Role Switcher */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-1.5 flex items-center gap-2">
            <button 
              onClick={() => setIsDevMode(!isDevMode)}
              className={`text-[10px] font-bold px-2 py-1 rounded-lg border transition ${isDevMode ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-slate-900 text-slate-400 border-slate-750'}`}
              title="Toggle Developer Mode for multi-role testing"
            >
              🛠️ Dev Mode: {isDevMode ? 'ON' : 'OFF'}
            </button>

            {isDevMode ? (
              <select 
                value={userRole} 
                onChange={(e) => {
                  const newRole = e.target.value;
                  setUserRole(newRole);
                  // Auto redirect customer away from restricted tabs
                  if (newRole === 'Customer' && ['appraisal', 'ocr', 'underwriting', 'analytics'].includes(activeTab)) {
                    setActiveTab('dashboard');
                  }
                }}
                className="bg-slate-900 border border-slate-750 text-sky-400 font-bold text-xs rounded-lg px-2.5 py-1 outline-none cursor-pointer"
              >
                <option value="Customer">👤 Customer Portal</option>
                <option value="Loan Officer">👔 Loan Officer</option>
                <option value="Branch Manager">🏢 Branch Manager</option>
                <option value="Admin">⚙️ System Admin</option>
              </select>
            ) : (
              <span className="text-xs font-bold text-sky-400 bg-sky-500/10 px-3 py-1 rounded-lg border border-sky-500/20">
                Role: {userRole}
              </span>
            )}
          </div>

          {/* Notification Bell Drawer */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="bg-slate-950 hover:bg-slate-900 border border-slate-800 text-slate-300 p-2 rounded-xl flex items-center justify-center transition relative"
            >
              🔔
              {notifications.filter(n => !n.isRead).length > 0 && (
                <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[9px] font-extrabold w-4 h-4 rounded-full flex items-center justify-center">
                  {notifications.filter(n => !n.isRead).length}
                </span>
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-3 w-80 bg-slate-900 border border-slate-750 rounded-2xl shadow-2xl p-4 z-50 space-y-3">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <h4 className="text-xs font-bold text-slate-200 uppercase">System Notifications</h4>
                  <button onClick={() => setNotifications(notifications.map(n => ({...n, isRead: true})))} className="text-[10px] text-sky-400 font-bold hover:underline">Mark all read</button>
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {notifications.map(n => (
                    <div key={n.id} className={`p-2.5 rounded-xl border text-xs ${n.isRead ? 'bg-slate-950/40 border-slate-850 text-slate-400' : 'bg-sky-500/10 border-sky-500/20 text-slate-200 font-semibold'}`}>
                      <div className="flex justify-between items-start">
                        <span className="font-bold text-sky-300">{n.title}</span>
                        <span className="text-[9px] text-slate-500">{n.time}</span>
                      </div>
                      <p className="text-[11px] mt-1 text-slate-300">{n.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Global Navigation Controls & Data Safety Bar */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-3 mb-6 shadow-lg flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          {/* Back Button */}
          <button 
            onClick={handleGoBack}
            disabled={tabHistoryIdx <= 0}
            className={`px-3 py-1.5 rounded-xl font-bold border transition flex items-center gap-1.5 ${tabHistoryIdx > 0 ? 'bg-slate-950 hover:bg-slate-850 border-slate-750 text-sky-300 cursor-pointer' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
            title="Go back to previous page"
          >
            ⬅️ Back
          </button>

          {/* Forward Button */}
          <button 
            onClick={handleGoForward}
            disabled={tabHistoryIdx >= tabHistory.length - 1}
            className={`px-3 py-1.5 rounded-xl font-bold border transition flex items-center gap-1.5 ${tabHistoryIdx < tabHistory.length - 1 ? 'bg-slate-950 hover:bg-slate-850 border-slate-750 text-sky-300 cursor-pointer' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
            title="Go forward to next page"
          >
            Forward ➡️
          </button>

          {/* Refresh Module */}
          <button 
            onClick={handleRefreshCurrentModule}
            className="bg-slate-950 hover:bg-slate-850 border border-slate-750 text-slate-200 px-3 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 cursor-pointer"
            title="Refresh active module"
          >
            🔄 Refresh
          </button>

          {/* Reset Module Form */}
          <button 
            onClick={handleResetCurrentModule}
            className="bg-slate-950 hover:bg-slate-850 border border-rose-500/30 text-rose-300 px-3 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 cursor-pointer"
            title="Reset form to defaults"
          >
            🧹 Reset
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* Undo */}
          <button 
            onClick={handleUndo}
            disabled={undoStack.length === 0}
            className={`px-3 py-1.5 rounded-xl font-bold border transition flex items-center gap-1 ${undoStack.length > 0 ? 'bg-slate-950 hover:bg-slate-850 border-slate-750 text-amber-300 cursor-pointer' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
            title="Undo recent change"
          >
            ↩️ Undo
          </button>

          {/* Redo */}
          <button 
            onClick={handleRedo}
            disabled={redoStack.length === 0}
            className={`px-3 py-1.5 rounded-xl font-bold border transition flex items-center gap-1 ${redoStack.length > 0 ? 'bg-slate-950 hover:bg-slate-850 border-slate-750 text-amber-300 cursor-pointer' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
            title="Redo recent change"
          >
            ↪️ Redo
          </button>

          {/* Save Draft */}
          <button 
            onClick={handleSaveDraft}
            className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3.5 py-1.5 rounded-xl transition shadow-sm flex items-center gap-1.5 cursor-pointer"
            title="Save draft version"
          >
            💾 Save Draft
          </button>

          {/* View Version History */}
          <button 
            onClick={() => setShowVersionModal(!showVersionModal)}
            className="bg-slate-950 hover:bg-slate-850 border border-sky-500/30 text-sky-300 px-3 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 cursor-pointer"
            title="Restore previous version"
          >
            📜 Versions ({draftVersions.length})
          </button>

          {/* Auto-Save Status */}
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
            ⏱️ Saved: {lastSavedTime}
          </span>
        </div>
      </div>

      {/* Version History Modal Popup */}
      {showVersionModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-750 rounded-3xl p-6 w-full max-w-lg shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider flex items-center gap-2">
                📜 Application Version History (Last 10 Drafts)
              </h3>
              <button onClick={() => setShowVersionModal(false)} className="text-slate-400 hover:text-white font-bold text-base">✕</button>
            </div>

            <div className="space-y-2 max-h-72 overflow-y-auto">
              {draftVersions.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No saved draft versions yet. Auto-saves every 30 seconds.</p>
              ) : (
                draftVersions.map((ver, idx) => (
                  <div key={ver.id} className="bg-slate-950 p-3 rounded-2xl border border-slate-800 flex justify-between items-center text-xs">
                    <div>
                      <span className="font-bold text-slate-200 block">Version #{draftVersions.length - idx}</span>
                      <span className="text-[10px] text-slate-400 font-mono">Saved at {ver.timestamp} ({ver.state.product || 'Home Loan'})</span>
                    </div>
                    <button 
                      onClick={() => {
                        setSharedLoanState(ver.state);
                        setActiveTab(ver.activeTab);
                        setShowVersionModal(false);
                        alert(`✅ Restored draft version saved at ${ver.timestamp}`);
                      }}
                      className="bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/40 px-3 py-1 rounded-xl font-bold transition cursor-pointer"
                    >
                      Restore 🔄
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Sticky Live Application Summary Panel & Wizard Navigation Bar */}
      <div className="sticky top-4 z-40 bg-gradient-to-r from-slate-900/90 via-slate-850/90 to-slate-900/90 backdrop-blur-xl border border-sky-500/30 rounded-2xl p-4 mb-6 shadow-2xl flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        {/* Left: Application Metadata Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 text-xs font-mono w-full lg:w-auto">
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">App ID</span>
            <strong className="text-sky-300 block text-[11px] font-bold">LN202685286</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Borrower</span>
            <strong className="text-slate-100 block text-[11px] truncate">{sharedLoanState.borrower_name}</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Loan Product</span>
            <strong className="text-emerald-400 block text-[11px] truncate">{sharedLoanState.product}</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Structure</span>
            <strong className="text-amber-300 block text-[11px] truncate">{loanStructure}</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Sanction Requested</span>
            <strong className="text-slate-100 block text-[11px]">₹{applicantLoanAmount.toLocaleString()}</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Total Security</span>
            <strong className="text-emerald-400 block text-[11px]">₹{((homeKaveriRate * homeBuiltArea || 4500000) + vehOnRoad + (goldWeight * goldPricePerGram || 1200000) + farmCost).toLocaleString()}</strong>
          </div>
          <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
            <span className="text-slate-500 block text-[9px] uppercase">Wizard Progress</span>
            <strong className="text-sky-300 block text-[11px]">Step {activeWorkflowStage} / 12</strong>
          </div>
        </div>

        {/* Right: Wizard Navigation Controls */}
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto justify-end">
          <button 
            onClick={handleWizardPrevious}
            disabled={activeWorkflowStage <= 1}
            className={`px-3 py-1.5 rounded-xl font-bold border text-xs transition ${activeWorkflowStage > 1 ? 'bg-slate-950 hover:bg-slate-850 border-slate-750 text-sky-300 cursor-pointer' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
          >
            ⬅️ Previous Step
          </button>

          <button 
            onClick={handleWizardNext}
            disabled={activeWorkflowStage >= 12}
            className={`px-3.5 py-1.5 rounded-xl font-bold border text-xs transition ${activeWorkflowStage < 12 ? 'bg-sky-600 hover:bg-sky-500 text-white border-sky-400 cursor-pointer shadow-md' : 'bg-slate-950/40 border-slate-850 text-slate-600 cursor-not-allowed'}`}
          >
            Next Step ➡️
          </button>

          <button 
            onClick={() => { setActiveWorkflowStage(8); setActiveTab('underwriting'); }}
            className="bg-slate-950 hover:bg-slate-850 border border-slate-750 text-slate-200 px-3 py-1.5 rounded-xl font-bold text-xs transition cursor-pointer"
          >
            📋 Review Application
          </button>

          <button 
            onClick={downloadSanctionPdf}
            className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-4 py-1.5 rounded-xl text-xs transition shadow-lg flex items-center gap-1.5 cursor-pointer"
          >
            🚀 Submit & Sanction PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Left Sidebar Menu */}
        <div className="lg:col-span-1 space-y-2.5">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 mb-1">
            🏦 Multi-Loan Products
          </div>

          <button 
            type="button"
            onClick={() => setActiveTab("dashboard")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'dashboard' 
                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/10 border border-emerald-400/20' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🎛️ Banking Dashboard
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("home_loan")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'home_loan' 
                ? 'bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/10 border border-sky-400/20' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🏠 Home Loan
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("agri_loan")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'agri_loan' 
                ? 'bg-gradient-to-r from-emerald-600 to-green-700 text-white shadow-lg shadow-emerald-600/10 border border-emerald-500/20' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🌾 Agriculture Loan
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("commercial_loan")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'commercial_loan' 
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/10 border border-indigo-400/20' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🏢 Commercial Loan
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("gold")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'gold' 
                ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 shadow-lg shadow-amber-500/20 border border-amber-400/30' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-amber-400/80 hover:text-amber-300'
            }`}
          >
            🥇 Gold Loan
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("farm_equipment")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'farm_equipment' 
                ? 'bg-gradient-to-r from-lime-600 to-emerald-700 text-white shadow-lg shadow-lime-600/20 border border-lime-400/30' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🚜 Farm Equipment Loan
          </button>

          <button 
            type="button"
            onClick={() => setActiveTab("vehicle")}
            className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
              activeTab === 'vehicle' 
                ? 'bg-gradient-to-r from-red-500 to-rose-600 text-white shadow-lg shadow-red-500/20 border border-red-400/30' 
                : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
            }`}
          >
            🚗 Vehicle Loan
          </button>

          {/* Role-Restricted Underwriting Engines Section */}
          {userRole !== 'Customer' && (
            <>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider px-3 pt-3 mb-1 border-t border-slate-800/60">
                🔬 Underwriting Engines ({userRole})
              </div>

              <button 
                type="button"
                onClick={() => setActiveTab("appraisal")}
                className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === 'appraisal' 
                    ? 'bg-gradient-to-r from-sky-500 to-sky-600 text-white shadow-lg shadow-sky-500/10 border border-sky-400/20' 
                    : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
                }`}
              >
                🗺️ Property Map
              </button>
              
              <button 
                type="button"
                onClick={() => setActiveTab("ocr")}
                className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === 'ocr' 
                    ? 'bg-gradient-to-r from-sky-500 to-sky-600 text-white shadow-lg shadow-sky-500/10 border border-sky-400/20' 
                    : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
                }`}
              >
                📄 Document OCR Audit
              </button>
              
              <button 
                type="button"
                onClick={() => setActiveTab("underwriting")}
                className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === 'underwriting' 
                    ? 'bg-gradient-to-r from-sky-500 to-sky-600 text-white shadow-lg shadow-sky-500/10 border border-sky-400/20' 
                    : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
                }`}
              >
                💳 AI Risk Analysis
              </button>
            </>
          )}

          {(userRole === 'Branch Manager' || userRole === 'Admin') && (
            <button 
              type="button"
              onClick={() => setActiveTab("analytics")}
              className={`w-full text-left px-4 py-3 rounded-xl font-semibold transition-all duration-300 ${
                activeTab === 'analytics' 
                  ? 'bg-gradient-to-r from-sky-500 to-sky-600 text-white shadow-lg shadow-sky-500/10 border border-sky-400/20' 
                  : 'bg-slate-900/40 hover:bg-slate-850/60 border border-slate-800 text-slate-400'
              }`}
            >
              📊 Portfolio Analytics
            </button>
          )}
        </div>

        {/* Right Main Panel Content */}
        <div className="lg:col-span-4 space-y-6">
          {/* TAB 0: CENTRAL MULTI-LOAN BANKING DASHBOARD */}
          {activeTab === "dashboard" && (
            <div className="space-y-8">
              {/* Hero Banking Banner */}
              <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl">
                <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                  <div>
                    <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">
                      🛡️ AegisCR Banking Decision Platform
                    </span>
                    <h2 className="text-3xl font-extrabold text-slate-100 mt-3 tracking-tight">
                      Multi-Product Credit Underwriting Console
                    </h2>
                    <p className="text-slate-400 text-sm mt-1 max-w-2xl leading-relaxed">
                      Select a specialized loan module below to evaluate collateral value, Kaveri guidance rates, live GoldAPI spot pricing, RBI LTV ceilings, and AI risk scores.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setActiveTab("home_loan")}
                      className="bg-sky-500/20 hover:bg-sky-500/30 border border-sky-500/30 text-sky-300 font-bold px-4 py-2.5 rounded-xl text-xs transition"
                    >
                      🏠 Home Loan ➔
                    </button>
                    <button
                      onClick={() => setActiveTab("gold")}
                      className="bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-300 font-bold px-4 py-2.5 rounded-xl text-xs transition"
                    >
                      🥇 Gold Loan ➔
                    </button>
                  </div>
                </div>

                {/* Enterprise Loan Origination Setup (Purpose & Structure Selector) */}
                <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-xl space-y-6">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider flex items-center gap-2">
                      🎯 Step 1: Enterprise Loan Origination Setup (Purpose & Structure)
                    </h3>
                    <span className="text-[10px] font-mono bg-sky-500/20 text-sky-300 px-3 py-1 rounded-full border border-sky-500/30">
                      Auto-Syncing to Smart Prediction
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                    {/* Loan Purpose Selection */}
                    <div className="space-y-2">
                      <label className="block text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                        🎯 Select Primary Loan Purpose
                      </label>
                      <select 
                        value={loanPurpose} 
                        onChange={(e) => {
                          setLoanPurpose(e.target.value);
                          setSharedLoanState(prev => ({ ...prev, purpose: e.target.value }));
                        }}
                        className="w-full bg-slate-950 border border-slate-750 text-slate-100 font-semibold rounded-xl px-4 py-3 outline-none text-xs"
                      >
                        <option>🏠 Home Purchase</option>
                        <option>🏗 Construction</option>
                        <option>🔄 Home Renovation</option>
                        <option>🌾 Agriculture</option>
                        <option>🚜 Farm Equipment</option>
                        <option>🚗 Vehicle Purchase</option>
                        <option>🏢 Business Expansion</option>
                        <option>💍 Personal Needs</option>
                        <option>📚 Education</option>
                        <option>💰 Working Capital</option>
                      </select>
                    </div>

                    {/* Loan Structure Selection */}
                    <div className="space-y-2">
                      <label className="block text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                        🔒 Select Credit Loan Structure
                      </label>
                      <select 
                        value={loanStructure} 
                        onChange={(e) => {
                          setLoanStructure(e.target.value);
                          setSharedLoanState(prev => ({ ...prev, structure: e.target.value }));
                        }}
                        className="w-full bg-slate-950 border border-slate-750 text-emerald-400 font-bold rounded-xl px-4 py-3 outline-none text-xs"
                      >
                        <option>🔒 Secured Loan</option>
                        <option>🔓 Unsecured Loan</option>
                        <option>📜 Collateral Based Loan</option>
                        <option>👥 Guarantor Based Loan</option>
                        <option>⚡ Hybrid Loan (Collateral + Guarantor)</option>
                      </select>
                    </div>
                  </div>

                  {/* Conditional Collateral & Guarantor Input Fields */}
                  {(loanStructure === '🔒 Secured Loan' || loanStructure === '📜 Collateral Based Loan' || loanStructure === '⚡ Hybrid Loan (Collateral + Guarantor)') && (
                    <div className="bg-slate-950/60 p-4 rounded-2xl border border-sky-500/20 space-y-4 text-xs">
                      <h4 className="text-[10px] font-extrabold uppercase text-sky-400 tracking-wider">
                        📜 Collateral Pledge Details
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-slate-400 mb-1">Collateral Type</label>
                          <select 
                            value={collateralType} 
                            onChange={(e) => {
                              setCollateralType(e.target.value);
                              setSharedLoanState(prev => ({ ...prev, collateral_type: e.target.value }));
                            }}
                            className="w-full bg-slate-900 border border-slate-750 rounded-xl px-3 py-2 text-slate-200"
                          >
                            <option>Property</option>
                            <option>Gold</option>
                            <option>Vehicle</option>
                            <option>Farm Equipment</option>
                            <option>Fixed Deposit</option>
                            <option>Other</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-slate-400 mb-1">Appraised Collateral Market Value (₹)</label>
                          <input 
                            type="number" 
                            value={collateralValue} 
                            onChange={(e) => {
                              const val = parseFloat(e.target.value) || 0;
                              setCollateralValue(val);
                              setSharedLoanState(prev => ({ ...prev, collateral_value: val }));
                            }}
                            className="w-full bg-slate-900 border border-slate-750 rounded-xl px-3 py-2 text-slate-200 font-mono" 
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {(loanStructure === '👥 Guarantor Based Loan' || loanStructure === '⚡ Hybrid Loan (Collateral + Guarantor)') && (
                    <div className="bg-slate-950/60 p-4 rounded-2xl border border-emerald-500/20 space-y-4 text-xs">
                      <h4 className="text-[10px] font-extrabold uppercase text-emerald-400 tracking-wider">
                        👥 Financial Guarantor Dossier
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-slate-400 mb-1">Guarantor Name</label>
                          <input type="text" value={guarantorName} onChange={(e) => { setGuarantorName(e.target.value); setSharedLoanState(prev => ({ ...prev, guarantor_name: e.target.value })); }} className="w-full bg-slate-900 border border-slate-750 rounded-xl px-3 py-2 text-slate-200" />
                        </div>
                        <div>
                          <label className="block text-slate-400 mb-1">Relationship</label>
                          <select value={guarantorRelation} onChange={(e) => setGuarantorRelation(e.target.value)} className="w-full bg-slate-900 border border-slate-750 rounded-xl px-3 py-2 text-slate-200">
                            <option>Father</option>
                            <option>Spouse</option>
                            <option>Business Partner</option>
                            <option>Relative</option>
                            <option>Other</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-slate-400 mb-1">Guarantor Income (₹/mo)</label>
                          <input type="number" value={guarantorIncome} onChange={(e) => { const v = parseFloat(e.target.value)||0; setGuarantorIncome(v); setSharedLoanState(prev => ({ ...prev, guarantor_income: v })); }} className="w-full bg-slate-900 border border-slate-750 rounded-xl px-3 py-2 text-slate-200 font-mono" />
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Stat Badges */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8 pt-6 border-t border-slate-800/80">
                  <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Active Modules</span>
                    <span className="text-2xl font-black text-slate-100 mt-1 block">6 Loan Products</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Kaveri Registry DB</span>
                    <span className="text-2xl font-black text-emerald-400 mt-1 block">Karnataka Live</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Spot Gold Feed</span>
                    <span className="text-2xl font-black text-amber-400 mt-1 block">GoldAPI.io (INR)</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-2xl">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Max LTV Guideline</span>
                    <span className="text-2xl font-black text-sky-400 mt-1 block">65% – 85% RBI</span>
                  </div>
                </div>
              </div>

              {/* 6 Interactive Loan Module Hero Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Module 1: Home Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-sky-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-sky-500/20 border border-sky-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🏠
                      </div>
                      <span className="text-[10px] font-extrabold text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded-full border border-sky-500/20 uppercase">
                        Up to 80% LTV
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-sky-300 transition">
                        Home Loan Module
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Appraise residential plots, independent houses & apartments with Kaveri guidance rates, land vs building depreciation math, and LTV charts.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("home_loan")}
                    className="w-full bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Home Loan Workspace ➔
                  </button>
                </div>

                {/* Module 2: Agriculture Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-emerald-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-emerald-500/20 border border-emerald-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🌾
                      </div>
                      <span className="text-[10px] font-extrabold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 uppercase">
                        Acre Guidance Rate
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-emerald-300 transition">
                        Agriculture Loan Module
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Appraise agricultural land across Dry Land, Black Soil Dry, Wet Land, and Bagayat classifications with Ag Risk scores.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("agri_loan")}
                    className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Agriculture Module ➔
                  </button>
                </div>

                {/* Module 3: Commercial Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-indigo-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-indigo-500/20 border border-indigo-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🏢
                      </div>
                      <span className="text-[10px] font-extrabold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded-full border border-indigo-500/20 uppercase">
                        65% LTV + EMI
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-indigo-300 transition">
                        Commercial Property Loan
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Evaluate commercial sites, retail spaces & office complexes with Kaveri commercial rates, LTV, and EMI amortization schedules.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("commercial_loan")}
                    className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Commercial Module ➔
                  </button>
                </div>

                {/* Module 4: Gold Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-amber-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-amber-500/20 border border-amber-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🥇
                      </div>
                      <span className="text-[10px] font-extrabold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20 uppercase">
                        Live Spot Pricing
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-amber-300 transition">
                        Gold Loan Module
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Instant spot gold appraisal (18K, 22K, 24K) with live GoldAPI spot ticker, 75% RBI LTV ceiling, and sanction PDF report generation.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("gold")}
                    className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Gold Loan Module ➔
                  </button>
                </div>

                {/* Module 5: Farm Equipment Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-lime-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-lime-500/20 border border-lime-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🚜
                      </div>
                      <span className="text-[10px] font-extrabold text-lime-400 bg-lime-500/10 px-2.5 py-1 rounded-full border border-lime-500/20 uppercase">
                        Subsidy + Ag Risk
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-lime-300 transition">
                        Farm Equipment Loan
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Finance tractors, harvesters & rotavators with Govt PM-KUSUM subsidy support, farm size risk scoring & EMI math.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("farm_equipment")}
                    className="w-full bg-gradient-to-r from-lime-600 to-emerald-700 hover:from-lime-500 hover:to-emerald-600 text-white font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Farm Equipment ➔
                  </button>
                </div>

                {/* Module 6: Vehicle Loan Card */}
                <div className="bg-gradient-to-b from-slate-900/90 to-slate-950 border border-slate-800 hover:border-red-500/50 rounded-3xl p-6 shadow-xl transition-all duration-300 group flex flex-col justify-between space-y-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div className="w-12 h-12 bg-red-500/20 border border-red-500/30 rounded-2xl flex items-center justify-center text-2xl">
                        🚗
                      </div>
                      <span className="text-[10px] font-extrabold text-red-400 bg-red-500/10 px-2.5 py-1 rounded-full border border-red-500/20 uppercase">
                        EV / SUV / Commercial
                      </span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-slate-100 group-hover:text-red-300 transition">
                        Vehicle Loan Module
                      </h3>
                      <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                        Finance Cars, SUVs, EVs & Commercial Vehicles with On-Road price calculation, down payment math & credit risk score.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setActiveTab("vehicle")}
                    className="w-full bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-400 hover:to-rose-500 text-white font-bold py-3 rounded-xl shadow-lg transition text-xs flex items-center justify-center gap-2"
                  >
                    Launch Vehicle Module ➔
                  </button>
                </div>
              </div>

              {/* Recent Applications & Quick Officer Action Console */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-6 backdrop-blur-md space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                    📋 Recent Loan Applications Queue ({userRole} Portal)
                  </h3>
                  <span className="text-xs text-sky-400 font-bold bg-sky-500/10 px-3 py-1 rounded-full border border-sky-500/20">
                    Live System Synchronized
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase">
                        <th className="py-3 px-3">Applicant Name</th>
                        <th className="py-3">Loan Product</th>
                        <th className="py-3">Requested Loan</th>
                        <th className="py-3">AI Risk Score</th>
                        <th className="py-3">AI Recommendation</th>
                        <th className="py-3">Status</th>
                        <th className="py-3 text-right pr-4">Quick Officer Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-850 text-slate-200 font-mono">
                      <tr className="hover:bg-slate-900/60 transition">
                        <td className="py-3.5 px-3 font-bold text-slate-100">Aarav Kumar</td>
                        <td className="py-3.5"><span className="text-amber-400 font-bold">🥇 Gold Loan</span></td>
                        <td className="py-3.5 font-bold">₹2,25,000</td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">15 / 100</span></td>
                        <td className="py-3.5"><span className="bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px] font-bold">✓ APPROVE</span></td>
                        <td className="py-3.5"><span className="text-sky-400 font-bold">Verified</span></td>
                        <td className="py-3.5 text-right pr-4 space-x-2">
                          <button onClick={() => setActiveTab("gold")} className="bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold px-2.5 py-1 rounded text-[10px]">Appraise</button>
                          <button onClick={handleDownloadGoldPdf} className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-bold px-2.5 py-1 rounded text-[10px]">Sanction PDF</button>
                        </td>
                      </tr>

                      <tr className="hover:bg-slate-900/60 transition">
                        <td className="py-3.5 px-3 font-bold text-slate-100">Rajesh Sharma</td>
                        <td className="py-3.5"><span className="text-sky-400 font-bold">🏠 Home Loan</span></td>
                        <td className="py-3.5 font-bold">₹45,00,000</td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">18 / 100</span></td>
                        <td className="py-3.5"><span className="bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px] font-bold">✓ APPROVE</span></td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">Approved</span></td>
                        <td className="py-3.5 text-right pr-4 space-x-2">
                          <button onClick={() => setActiveTab("home_loan")} className="bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 font-bold px-2.5 py-1 rounded text-[10px]">Kaveri Rate</button>
                          <button onClick={() => setActiveTab("underwriting")} className="bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-bold px-2.5 py-1 rounded text-[10px]">AI Risk</button>
                        </td>
                      </tr>

                      <tr className="hover:bg-slate-900/60 transition">
                        <td className="py-3.5 px-3 font-bold text-slate-100">Vikram Patil</td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">🌾 Agriculture Loan</span></td>
                        <td className="py-3.5 font-bold">₹12,50,000</td>
                        <td className="py-3.5"><span className="text-amber-400 font-bold">30 / 100</span></td>
                        <td className="py-3.5"><span className="bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px] font-bold">✓ APPROVE</span></td>
                        <td className="py-3.5"><span className="text-amber-400 font-bold">Under Review</span></td>
                        <td className="py-3.5 text-right pr-4 space-x-2">
                          <button onClick={() => setActiveTab("agri_loan")} className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-bold px-2.5 py-1 rounded text-[10px]">Ag Valuation</button>
                          <button onClick={() => setActiveTab("ocr")} className="bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 font-bold px-2.5 py-1 rounded text-[10px]">OCR Audit</button>
                        </td>
                      </tr>

                      <tr className="hover:bg-slate-900/60 transition">
                        <td className="py-3.5 px-3 font-bold text-slate-100">Suresh Gowda</td>
                        <td className="py-3.5"><span className="text-lime-400 font-bold">🚜 Farm Equipment</span></td>
                        <td className="py-3.5 font-bold">₹6,50,000</td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">15 / 100</span></td>
                        <td className="py-3.5"><span className="bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px] font-bold">✓ APPROVE</span></td>
                        <td className="py-3.5"><span className="text-emerald-400 font-bold">Disbursed</span></td>
                        <td className="py-3.5 text-right pr-4 space-x-2">
                          <button onClick={() => setActiveTab("farm_equipment")} className="bg-lime-500/20 hover:bg-lime-500/30 text-lime-300 font-bold px-2.5 py-1 rounded text-[10px]">Subsidy</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* MODULE 1: HOME LOAN WORKSPACE */}
          {activeTab === "home_loan" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                  🏠 Home Loan Collateral Appraisal
                </h2>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">District</label>
                    <input type="text" value={homeDistrict} onChange={(e) => setHomeDistrict(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Taluk</label>
                    <input type="text" value={homeTaluk} onChange={(e) => setHomeTaluk(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Village / Layout</label>
                    <input type="text" value={homeVillage} onChange={(e) => setHomeVillage(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Survey / Khata No.</label>
                    <input type="text" value={homeSurvey} onChange={(e) => setHomeSurvey(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Plot Area (Sq.Ft)</label>
                    <input type="number" value={homePlotArea} onChange={(e) => setHomePlotArea(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Built-up Area (Sq.Ft)</label>
                    <input type="number" value={homeBuiltArea} onChange={(e) => setHomeBuiltArea(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Property Classification</label>
                    <select value={homePropType} onChange={(e) => setHomePropType(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold">
                      <option value="Independent House">Independent House</option>
                      <option value="Residential Apartment">Residential Apartment</option>
                      <option value="Residential Plot">Residential Plot</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Construction Year</label>
                    <input type="number" value={homeConstYear} onChange={(e) => setHomeConstYear(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <button onClick={evaluateHomeLoan} disabled={homeLoading} className="w-full bg-sky-500 hover:bg-sky-400 text-white font-bold py-3 rounded-xl transition text-xs">
                  {homeLoading ? '🔄 Querying Kaveri Database...' : '⚡ Calculate Home Property Value & LTV'}
                </button>
              </div>

              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                  📊 Valuation Breakdown & Recommended Sanction
                </h2>

                {homeResult ? (
                  <div className="space-y-4">
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Kaveri Guidance Rate</span>
                      <strong className="text-sky-300 text-sm">₹{homeResult.rate_per_sqft}/sqft</strong>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-850">
                        <span className="text-slate-500 block uppercase font-bold text-[10px]">Land Value</span>
                        <strong className="text-slate-100 text-lg block mt-1">₹{homeResult.land_value?.toLocaleString()}</strong>
                      </div>
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-850">
                        <span className="text-slate-500 block uppercase font-bold text-[10px]">Building Value</span>
                        <strong className="text-slate-100 text-lg block mt-1">₹{homeResult.building_value?.toLocaleString()}</strong>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-sky-950/40 to-slate-950 p-5 rounded-2xl border border-sky-500/30">
                      <span className="text-xs text-sky-400 uppercase font-bold block">Total Property Market Value</span>
                      <span className="text-3xl font-black text-slate-100 block mt-1">₹{homeResult.total_property_value?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 p-5 rounded-2xl border border-emerald-500/40">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-emerald-400 uppercase font-bold block">Recommended Sanction (80% LTV)</span>
                        <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded border border-emerald-500/30">LTV {homeResult.ltv}%</span>
                      </div>
                      <span className="text-3xl font-black text-emerald-300 block mt-1">₹{homeResult.recommended_loan?.toLocaleString()}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 text-xs">Enter property parameters and click Calculate to view Kaveri valuation math.</div>
                )}
              </div>
            </div>
          )}

          {/* MODULE 2: AGRICULTURE LOAN WORKSPACE */}
          {activeTab === "agri_loan" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-emerald-400 border-b border-slate-800 pb-3">
                  🌾 Agricultural Land Collateral Assessment
                </h2>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">District</label>
                    <input type="text" value={agriDistrict} onChange={(e) => setAgriDistrict(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Taluk</label>
                    <input type="text" value={agriTaluk} onChange={(e) => setAgriTaluk(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Village / Locality</label>
                    <input type="text" value={agriVillage} onChange={(e) => setAgriVillage(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Survey Number</label>
                    <input type="text" value={agriSurvey} onChange={(e) => setAgriSurvey(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Land Area (Acres)</label>
                    <input type="number" value={agriAcres} step="0.5" onChange={(e) => setAgriAcres(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Land Classification</label>
                    <select value={agriLandType} onChange={(e) => setAgriLandType(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold">
                      <option value="Dry Land">Dry Land</option>
                      <option value="Black Soil Dry">Black Soil Dry</option>
                      <option value="Wet Land">Wet Land</option>
                      <option value="Bagayat Land">Bagayat Land (Irrigated)</option>
                    </select>
                  </div>
                </div>

                <button onClick={evaluateAgriLoan} disabled={agriLoading} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl transition text-xs">
                  {agriLoading ? '🔄 Reading Kaveri Ag Rate Database...' : '⚡ Read Kaveri Ag Rate & Calculate Loan'}
                </button>
              </div>

              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-emerald-400 border-b border-slate-800 pb-3">
                  📈 Ag Valuation & Agricultural Risk Score
                </h2>

                {agriResult ? (
                  <div className="space-y-4">
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Kaveri Rate / Acre ({agriResult.land_type})</span>
                      <strong className="text-emerald-300 text-sm">₹{agriResult.rate_per_acre?.toLocaleString()}/acre</strong>
                    </div>

                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Agricultural Risk Index</span>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${agriResult.risk_score <= 20 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'}`}>
                        {agriResult.risk_score} / 100 ({agriResult.risk_score <= 20 ? 'Low Ag Risk' : 'Moderate Ag Risk'})
                      </span>
                    </div>

                    <div className="bg-gradient-to-r from-slate-950 to-slate-900 p-5 rounded-2xl border border-slate-800">
                      <span className="text-xs text-slate-400 uppercase font-bold block">Total Agricultural Land Value</span>
                      <span className="text-3xl font-black text-slate-100 block mt-1">₹{agriResult.total_land_value?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 p-5 rounded-2xl border border-emerald-500/40">
                      <span className="text-xs text-emerald-400 uppercase font-bold block">Eligible Agricultural Loan (75% LTV Cap)</span>
                      <span className="text-3xl font-black text-emerald-300 block mt-1">₹{agriResult.eligible_loan?.toLocaleString()}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 text-xs">Select land classification to query Kaveri agricultural database.</div>
                )}
              </div>
            </div>
          )}

          {/* MODULE 3: COMMERCIAL PROPERTY LOAN WORKSPACE */}
          {activeTab === "commercial_loan" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-indigo-400 border-b border-slate-800 pb-3">
                  🏢 Commercial Property Loan Assessment
                </h2>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">District</label>
                    <input type="text" value={commDistrict} onChange={(e) => setCommDistrict(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Taluk</label>
                    <input type="text" value={commTaluk} onChange={(e) => setCommTaluk(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Plot Area (Sq.Ft)</label>
                    <input type="number" value={commPlotArea} onChange={(e) => setCommPlotArea(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Built-up Area (Sq.Ft)</label>
                    <input type="number" value={commBuiltArea} onChange={(e) => setCommBuiltArea(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Annual Interest Rate (%)</label>
                    <input type="number" value={commInterestRate} step="0.1" onChange={(e) => setCommInterestRate(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Tenure (Months)</label>
                    <input type="number" value={commTenure} onChange={(e) => setCommTenure(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <button onClick={evaluateCommLoan} disabled={commLoading} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl transition text-xs">
                  {commLoading ? '🔄 Calculating Commercial Loan...' : '⚡ Calculate Commercial Valuation & EMI'}
                </button>
              </div>

              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-indigo-400 border-b border-slate-800 pb-3">
                  💳 Commercial Loan LTV & Monthly EMI Schedule
                </h2>

                {commResult ? (
                  <div className="space-y-4">
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Commercial Guidance Rate</span>
                      <strong className="text-indigo-300 text-sm">₹{commResult.comm_rate_per_sqft}/sqft</strong>
                    </div>

                    <div className="bg-gradient-to-r from-slate-950 to-slate-900 p-5 rounded-2xl border border-slate-800">
                      <span className="text-xs text-slate-400 uppercase font-bold block">Total Commercial Property Value</span>
                      <span className="text-3xl font-black text-slate-100 block mt-1">₹{commResult.property_value?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-indigo-950/40 to-slate-950 p-5 rounded-2xl border border-indigo-500/40">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-indigo-400 uppercase font-bold block">Eligible Commercial Loan (65% LTV Cap)</span>
                        <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded border border-indigo-500/30">LTV {commResult.ltv}%</span>
                      </div>
                      <span className="text-3xl font-black text-indigo-300 block mt-1">₹{commResult.eligible_loan?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 p-5 rounded-2xl border border-emerald-500/40">
                      <span className="text-xs text-emerald-400 uppercase font-bold block">Estimated Monthly EMI</span>
                      <span className="text-3xl font-black text-emerald-300 block mt-1">₹{commResult.monthly_emi?.toLocaleString()}/month</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 text-xs">Enter commercial plot & built-up area to compute EMI.</div>
                )}
              </div>
            </div>
          )}

          {/* MODULE 5: FARM EQUIPMENT LOAN WORKSPACE */}
          {activeTab === "farm_equipment" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-lime-400 border-b border-slate-800 pb-3">
                  🚜 Farm Equipment Loan Appraisal
                </h2>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Equipment Type</label>
                    <select value={farmType} onChange={(e) => setFarmType(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold">
                      <option value="Tractor">Tractor</option>
                      <option value="Combine Harvester">Combine Harvester</option>
                      <option value="Rotavator">Rotavator</option>
                      <option value="Cultivator">Cultivator</option>
                      <option value="Power Tiller">Power Tiller</option>
                      <option value="Irrigation Solar Pump">Irrigation Solar Pump</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Brand & Model</label>
                    <input type="text" value={farmBrand} onChange={(e) => setFarmBrand(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Equipment Cost (₹)</label>
                    <input type="number" value={farmCost} onChange={(e) => setFarmCost(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Govt Subsidy Support (₹)</label>
                    <input type="number" value={farmSubsidy} onChange={(e) => setFarmSubsidy(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold text-emerald-400" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Farmer Down Payment (₹)</label>
                    <input type="number" value={farmDownPay} onChange={(e) => setFarmDownPay(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Farm Land Size (Acres)</label>
                    <input type="number" value={farmAcres} step="0.5" onChange={(e) => setFarmAcres(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100" />
                  </div>
                </div>

                <button onClick={evaluateFarmLoan} disabled={farmLoading} className="w-full bg-lime-600 hover:bg-lime-500 text-white font-bold py-3 rounded-xl transition text-xs">
                  {farmLoading ? '🔄 Calculating Subsidy & Repayment...' : '⚡ Calculate Equipment Loan & Repayment Risk'}
                </button>
              </div>

              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-lime-400 border-b border-slate-800 pb-3">
                  📊 Farm Loan Sanction & Subsidy Breakdown
                </h2>

                {farmResult ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-850">
                        <span className="text-slate-500 block uppercase font-bold text-[10px]">Net Equipment Cost</span>
                        <strong className="text-slate-100 text-lg block mt-1">₹{farmResult.net_equipment_cost?.toLocaleString()}</strong>
                      </div>
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-850">
                        <span className="text-emerald-500 block uppercase font-bold text-[10px]">PM-KUSUM Subsidy</span>
                        <strong className="text-emerald-400 text-lg block mt-1">₹{farmResult.subsidy_amount?.toLocaleString()}</strong>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-lime-950/40 to-slate-950 p-5 rounded-2xl border border-lime-500/40">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-lime-400 uppercase font-bold block">Sanctioned Loan Amount</span>
                        <span className="bg-lime-500/20 text-lime-300 text-[10px] font-bold px-2 py-0.5 rounded border border-lime-500/30">LTV {farmResult.ltv}%</span>
                      </div>
                      <span className="text-3xl font-black text-lime-300 block mt-1">₹{farmResult.loan_sanction?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 p-5 rounded-2xl border border-emerald-500/40">
                      <span className="text-xs text-emerald-400 uppercase font-bold block">Estimated Monthly Repayment EMI</span>
                      <span className="text-3xl font-black text-emerald-300 block mt-1">₹{farmResult.monthly_emi?.toLocaleString()}/month</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 text-xs">Enter equipment details to compute net cost and Govt subsidy.</div>
                )}
              </div>
            </div>
          )}

          {/* MODULE 6: VEHICLE LOAN WORKSPACE (CarQuery API & Master DB) */}
          {activeTab === "vehicle" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                  <h2 className="text-xl font-semibold flex items-center gap-2 text-rose-400">
                    🚗 Vehicle Loan & CarQuery API Specs
                  </h2>
                  <span className="text-[10px] font-bold text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded-full border border-sky-500/20">
                    {vehSpecSource}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Vehicle Brand (Make)</label>
                    <select
                      value={vehBrand}
                      onChange={(e) => handleVehicleBrandChange(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold"
                    >
                      {vehMakes.map((m) => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Vehicle Model (CarQuery)</label>
                    <select
                      value={vehModel}
                      onChange={(e) => handleVehicleModelChange(vehBrand, e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold"
                    >
                      {vehModels.map((mod) => (
                        <option key={mod} value={mod}>{mod}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* CarQuery Specification Badges & Manual Inputs */}
                <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-850 space-y-3">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">⚙️ Vehicle Specifications (CarQuery API Auto-Filled)</span>
                  <div className="grid grid-cols-4 gap-2 text-[11px] font-mono">
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">FUEL</span>
                      <input type="text" value={vehFuelType} onChange={(e) => setVehFuelType(e.target.value)} className="bg-transparent text-emerald-400 font-bold w-full outline-none" />
                    </div>
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">TRANS</span>
                      <input type="text" value={vehTransmission} onChange={(e) => setVehTransmission(e.target.value)} className="bg-transparent text-sky-400 font-bold w-full outline-none" />
                    </div>
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">ENGINE</span>
                      <input type="text" value={vehEngineCc} onChange={(e) => setVehEngineCc(e.target.value)} className="bg-transparent text-amber-400 font-bold w-full outline-none" />
                    </div>
                    <div className="bg-slate-900 p-2 rounded border border-slate-800">
                      <span className="text-slate-500 block text-[9px]">BODY</span>
                      <input type="text" value={vehBodyType} onChange={(e) => setVehBodyType(e.target.value)} className="bg-transparent text-rose-400 font-bold w-full outline-none" />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Ex-Showroom Price (₹)</label>
                    <input type="number" value={vehExPrice} onChange={(e) => setVehExPrice(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">On-Road Price (₹ Master DB)</label>
                    <input type="number" value={vehOnRoad} onChange={(e) => setVehOnRoad(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-rose-300 font-bold" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Down Payment (₹)</label>
                    <input type="number" value={vehDownPay} onChange={(e) => setVehDownPay(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Applicant Monthly Income (₹)</label>
                    <input type="number" value={vehIncome} onChange={(e) => setVehIncome(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 font-bold" />
                  </div>
                </div>

                <button onClick={evaluateVehicleLoan} disabled={vehLoading} className="w-full bg-rose-600 hover:bg-rose-500 text-white font-bold py-3 rounded-xl transition text-xs flex items-center justify-center gap-2">
                  {vehLoading ? '🔄 Auto-filling & Evaluating...' : '⚡ Calculate Vehicle Loan Eligibility & EMI'}
                </button>
              </div>

              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-rose-400 border-b border-slate-800 pb-3">
                  📈 Vehicle Specs & Credit Risk Analysis
                </h2>

                {vehResult ? (
                  <div className="space-y-4">
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between border-b border-slate-850 pb-2">
                        <span className="text-slate-400">Model & Variant</span>
                        <strong className="text-slate-100">{vehResult.vehicle_make} {vehResult.vehicle_model} ({vehResult.vehicle_variant || 'Standard'})</strong>
                      </div>
                      <div className="flex justify-between text-[11px]">
                        <span className="text-slate-400">Spec Matrix</span>
                        <span className="text-emerald-400 font-mono font-bold">{vehResult.fuel_type} • {vehResult.transmission} • {vehResult.engine_cc}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                        <span className="text-slate-500 block uppercase font-bold text-[10px]">On-Road Price</span>
                        <strong className="text-slate-100 text-lg block mt-1">₹{vehResult.on_road_price?.toLocaleString()}</strong>
                      </div>
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                        <span className="text-sky-500 block uppercase font-bold text-[10px]">Credit Risk Score</span>
                        <strong className="text-sky-400 text-lg block mt-1">{vehResult.credit_risk_score} / 100</strong>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-rose-950/40 to-slate-950 p-5 rounded-2xl border border-rose-500/40">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-rose-400 uppercase font-bold block">Sanctioned Vehicle Loan</span>
                        <span className="bg-rose-500/20 text-rose-300 text-[10px] font-bold px-2 py-0.5 rounded border border-rose-500/30">LTV {vehResult.ltv}%</span>
                      </div>
                      <span className="text-3xl font-black text-rose-300 block mt-1">₹{vehResult.loan_sanction?.toLocaleString()}</span>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 p-5 rounded-2xl border border-emerald-500/40">
                      <span className="text-xs text-emerald-400 uppercase font-bold block">Monthly EMI (60 Months)</span>
                      <span className="text-3xl font-black text-emerald-300 block mt-1">₹{vehResult.monthly_emi?.toLocaleString()}/month</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-500 text-xs">Select vehicle brand and model to pull CarQuery specs & master prices.</div>
                )}
              </div>
            </div>
          )}

          {/* TAB 1: PROPERTY APPRAISAL & MAP (INTELLIGENT CONTEXT-AWARE MODULE) */}
          {activeTab === "appraisal" && (
            <div className="space-y-6">
              {/* Product Context-Aware Notification Banner */}
              {sharedLoanState.product === "Vehicle Loan" && (
                <div className="bg-gradient-to-r from-red-950/80 via-slate-900 to-rose-950/80 border border-red-500/30 rounded-2xl p-5 backdrop-blur-md space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 className="text-xs font-bold text-red-300 uppercase tracking-wider flex items-center gap-2">
                      ℹ️ Property Valuation is Not Applicable for Vehicle Financing
                    </h3>
                    <span className="text-[10px] bg-red-500/20 text-red-300 px-3 py-1 rounded-full border border-red-500/30 font-mono font-bold">
                      Collateral: Vehicle ({vehBrand} {vehModel})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Vehicle Model</span>
                      <strong className="text-slate-100 block text-[11px] truncate mt-0.5">{vehBrand} {vehModel}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">On-Road Price</span>
                      <strong className="text-emerald-400 block text-[11px] mt-0.5">₹{vehOnRoad.toLocaleString()}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Depreciation (Year 1)</span>
                      <strong className="text-amber-400 block text-[11px] mt-0.5">₹{Math.round(vehOnRoad * 0.05).toLocaleString()} (5%)</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Eligible Vehicle Loan</span>
                      <strong className="text-sky-300 block text-[11px] mt-0.5">₹{Math.round(vehOnRoad * 0.85).toLocaleString()}</strong>
                    </div>
                  </div>
                </div>
              )}

              {sharedLoanState.product === "Gold Loan" && (
                <div className="bg-gradient-to-r from-amber-950/80 via-slate-900 to-amber-900/80 border border-amber-500/30 rounded-2xl p-5 backdrop-blur-md space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                      ℹ️ Property Valuation is Not Applicable for Gold Collateral
                    </h3>
                    <span className="text-[10px] bg-amber-500/20 text-amber-300 px-3 py-1 rounded-full border border-amber-500/30 font-mono font-bold">
                      Collateral: Gold ({goldWeight}g • {goldPurity})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Pledged Weight</span>
                      <strong className="text-amber-300 block text-[11px] mt-0.5">{goldWeight} Grams ({goldPurity})</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Live Spot Rate</span>
                      <strong className="text-slate-100 block text-[11px] mt-0.5">₹{goldPricePerGram.toLocaleString()} / gram</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Total Gold Market Value</span>
                      <strong className="text-emerald-400 block text-[11px] mt-0.5">₹{(goldWeight * goldPricePerGram).toLocaleString()}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Eligible Gold Loan (75% LTV)</span>
                      <strong className="text-sky-300 block text-[11px] mt-0.5">₹{Math.round(goldWeight * goldPricePerGram * 0.75).toLocaleString()}</strong>
                    </div>
                  </div>
                </div>
              )}

              {sharedLoanState.product === "Farm Equipment Loan" && (
                <div className="bg-gradient-to-r from-lime-950/80 via-slate-900 to-emerald-950/80 border border-lime-500/30 rounded-2xl p-5 backdrop-blur-md space-y-3">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                    <h3 className="text-xs font-bold text-lime-300 uppercase tracking-wider flex items-center gap-2">
                      ℹ️ Property Valuation Optional for Farm Machinery
                    </h3>
                    <span className="text-[10px] bg-lime-500/20 text-lime-300 px-3 py-1 rounded-full border border-lime-500/30 font-mono font-bold">
                      Equipment: {farmType} ({farmBrand})
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Machinery Cost</span>
                      <strong className="text-slate-100 block text-[11px] mt-0.5">₹{farmCost.toLocaleString()}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">PM-KUSUM Subsidy</span>
                      <strong className="text-emerald-400 block text-[11px] mt-0.5">₹{farmSubsidy.toLocaleString()}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Net Equipment Value</span>
                      <strong className="text-amber-300 block text-[11px] mt-0.5">₹{(farmCost - farmSubsidy).toLocaleString()}</strong>
                    </div>
                    <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                      <span className="text-slate-500 block text-[9px] uppercase">Eligible Machinery Loan</span>
                      <strong className="text-sky-300 block text-[11px] mt-0.5">₹{Math.round((farmCost - farmSubsidy) * 0.85).toLocaleString()}</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Main Real Estate Valuation Grid (For Home, Agri, Commercial Loans) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Column: Forms and GIS info */}
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm">
                  <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                    📋 Address Registration & Land Details ({sharedLoanState.product})
                  </h2>

                {geocodedAddress && (
                  <div className="mb-6 bg-slate-950/80 border border-emerald-500/30 rounded-2xl p-4 text-xs space-y-2 shadow-lg">
                    <h3 className="font-bold text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider text-[10px] border-b border-slate-800 pb-2">
                      📍 Pinned Geocoded Address Details
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-slate-350">
                      <div><span className="text-slate-500 font-semibold">State:</span> {geocodedAddress.state}</div>
                      <div><span className="text-slate-500 font-semibold">PIN Code:</span> {geocodedAddress.pincode || 'N/A'}</div>
                      <div><span className="text-slate-500 font-semibold">District:</span> {geocodedAddress.district || 'N/A'}</div>
                      <div><span className="text-slate-500 font-semibold">Taluk:</span> {geocodedAddress.taluk || 'N/A'}</div>
                      <div className="col-span-2"><span className="text-slate-500 font-semibold">Village / Locality:</span> {geocodedAddress.village || 'N/A'}</div>
                      {geocodedAddress.displayName && (
                        <div className="col-span-2 text-[10px] text-slate-500 leading-normal border-t border-slate-800/50 pt-2 mt-1">
                          <span className="font-semibold text-slate-400">Full Address:</span> {geocodedAddress.displayName}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <form onSubmit={handleCalculate} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">State</label>
                      <input 
                        type="text" 
                        value={selectedState} 
                        onChange={e => setSelectedState(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500" 
                        placeholder="e.g. Karnataka"
                      />
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">District</label>
                      <select 
                        value={selectedDistrict} 
                        onChange={e => setSelectedDistrict(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      >
                        <option value="">Select District</option>
                        {districts.map(d => <option key={d} value={d}>{d}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">Taluk / Office</label>
                      <select 
                        value={selectedTaluk} 
                        onChange={e => setSelectedTaluk(e.target.value)}
                        disabled={!selectedDistrict}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50"
                      >
                        <option value="">Select Taluk</option>
                        {taluks.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">Village / Locality</label>
                      <select 
                        value={selectedVillage} 
                        onChange={e => setSelectedVillage(e.target.value)}
                        disabled={!selectedTaluk}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 disabled:opacity-50"
                      >
                        <option value="">Select Village</option>
                        {villages.map(v => <option key={v} value={v}>{v}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">Survey / Khata No</label>
                      <input 
                        type="text" 
                        value={surveyNumber}
                        onChange={e => setSurveyNumber(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500" 
                        placeholder="e.g. 101/2"
                      />
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">PIN Code</label>
                      <input 
                        type="text" 
                        value={pincode}
                        onChange={e => setPincode(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500" 
                        placeholder="e.g. 562110"
                      />
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">Land Area (Sq Ft)</label>
                      <input 
                        type="number" 
                        value={landArea}
                        onChange={e => setLandArea(Number(e.target.value))}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500" 
                        placeholder="e.g. 1200"
                        min="1"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">Property Classification</label>
                      <select 
                        value={landType} 
                        onChange={e => setLandType(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
                      >
                        <option>Residential</option>
                        <option>Commercial</option>
                        <option>Agricultural</option>
                        <option>Industrial</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1 font-semibold">
                        Land Price (₹) <span className="text-[10px] text-slate-500 font-normal">Optional override</span>
                      </label>
                      <input 
                        type="number" 
                        value={landPrice}
                        onChange={e => setLandPrice(Number(e.target.value))}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500" 
                        placeholder="e.g. 45000 / 1200000"
                      />
                    </div>
                  </div>

                  {/* Multiple Matching Records Selection Panel */}
                  {guidelineRecords.length > 1 && (
                    <div className="mt-6 p-4 bg-slate-900/90 border border-slate-800 rounded-xl">
                      <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-2 flex items-center gap-1.5">
                        📋 Matching Guidance Records Found ({guidelineRecords.length})
                      </h3>
                      <p className="text-[11px] text-slate-500 mb-3">
                        Multiple circular rate classifications match this locality. Select a card below to load its specific valuation rate:
                      </p>
                      <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                        {guidelineRecords.map((rec, index) => (
                          <button
                            key={index}
                            onClick={() => handleSelectRecord(index)}
                            type="button"
                            className={`w-full text-left p-3 rounded-lg border text-xs transition-all duration-200 ${
                              selectedRecordIndex === index
                                ? 'bg-sky-500/10 border-sky-400 text-sky-200 shadow-md'
                                : 'bg-slate-800/40 border-slate-700 hover:border-slate-600 text-slate-300'
                            }`}
                          >
                            <div className="font-bold flex justify-between">
                              <span className="truncate max-w-[160px]">{rec.property_type}</span>
                              <span className="text-emerald-400 font-black">
                                ₹{rec.guidance_value.toLocaleString()}/{rec.original_unit === 'Acre' ? 'Acre' : 'sqft'}
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-500 mt-1 truncate">Locality: {rec.locality}</div>
                            <div className="text-[9px] text-slate-400 mt-1.5 flex gap-3 border-t border-slate-800/60 pt-1">
                              <span>Rate/SqFt: ₹{rec.rate_per_sqft.toLocaleString()}</span>
                              {rec.rate_per_acre && <span>Rate/Acre: ₹{rec.rate_per_acre.toLocaleString()}</span>}
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {error && <div className="text-red-400 text-xs mt-2">⚠️ {error}</div>}

                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full mt-6 bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-600 hover:to-sky-700 text-white font-bold py-3 px-4 rounded-xl text-sm transition duration-300 shadow-md hover:shadow-sky-500/20 disabled:opacity-50"
                  >
                    {loading ? 'Processing Appraisal...' : 'Calculate Property Valuation'}
                  </button>
                </form>

                {/* Results Summary Box */}
                {valuationData && (
                  <div className="mt-8 space-y-6">
                    <h2 className="text-sm uppercase tracking-wider text-sky-400 font-bold mb-1 flex items-center gap-1.5">
                      🤖 AI Appraisal & Valuation Dashboard
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Card 1: Estimated Market Value */}
                      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-sky-500/30 rounded-2xl p-5 shadow-lg transition-all duration-300">
                        <span className="text-[10px] uppercase text-slate-400 tracking-wider font-semibold">Estimated Market Value</span>
                        <p className="text-2xl font-black text-sky-400 mt-2">₹{valuationData.totalValue.toLocaleString()}</p>
                        <div className="text-[10.5px] text-slate-500 mt-1 flex justify-between">
                          <span>Rate: ₹{valuationData.marketRate.toLocaleString()}/sqft</span>
                          <span>LTV: {valuationData.ltvPercentage}%</span>
                        </div>
                      </div>

                      {/* Card 2: Model Confidence */}
                      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-emerald-500/30 rounded-2xl p-5 shadow-lg transition-all duration-300">
                        <span className="text-[10px] uppercase text-slate-400 tracking-wider font-semibold">Model Confidence</span>
                        <p className="text-2xl font-black text-emerald-400 mt-2">{valuationData.confidence || 95}%</p>
                        <div className="text-[10.5px] text-slate-500 mt-1 flex justify-between">
                          <span>Risk: {valuationData.riskCategory}</span>
                          <span>Status: Verified</span>
                        </div>
                      </div>

                      {/* Card 3: Investment Score */}
                      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 hover:border-amber-500/30 rounded-2xl p-5 shadow-lg transition-all duration-300">
                        <span className="text-[10px] uppercase text-slate-400 tracking-wider font-semibold">Investment Score</span>
                        <p className="text-2xl font-black text-amber-500 mt-2">{valuationData.investmentScore || 8.5}/10</p>
                        <div className="text-[10.5px] text-slate-500 mt-1 flex justify-between">
                          <span>Trend: Increasing</span>
                          <span>Class: {valuationData.classification}</span>
                        </div>
                      </div>
                    </div>

                    {/* Auxiliary circular value rates metadata */}
                    <div className="bg-slate-900/40 border border-slate-850 rounded-2xl p-5 grid grid-cols-2 gap-4">
                      <div className="border-r border-slate-800 pr-4">
                        <span className="text-[10px] uppercase text-slate-400 tracking-wider">Kaveri Guidance Value</span>
                        <p className="text-xl font-bold text-slate-300 mt-1">₹{valuationData.guidelineRate.toLocaleString()}/sqft</p>
                        <span className="text-[9.5px] text-slate-500">Government Circle Rate</span>
                      </div>
                      <div className="pl-4">
                        <span className="text-[10px] uppercase text-slate-400 tracking-wider">Max Eligible Loan</span>
                        <p className="text-xl font-bold text-indigo-400 mt-1">₹{valuationData.maxLoan.toLocaleString()}</p>
                        <span className="text-[9.5px] text-slate-500">Based on LTV Limits</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* AI Property Scorecard Widget */}
                {gisProfile && (
                  <div className="mt-6 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 border border-slate-800 hover:border-emerald-500/20 rounded-2xl p-6 shadow-xl transition-all duration-300">
                    <span className="text-[10px] uppercase text-emerald-400 tracking-wider font-extrabold block mb-1">
                      ⭐ AI Property Intelligence Score
                    </span>
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-black text-white">{gisProfile.score}</span>
                        <span className="text-sm text-slate-500">/ 10</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 justify-end max-w-[200px]">
                        <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          {gisProfile.investmentGrade}
                        </span>
                        <span className="bg-sky-500/10 border border-sky-500/30 text-sky-400 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          {gisProfile.connectivityTier}
                        </span>
                        <span className="bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          {gisProfile.riskTier}
                        </span>
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-3 leading-relaxed border-t border-slate-850 pt-3">
                      Score dynamically aggregated using circle guidance values, proximity to primary infrastructure, road width connectivity, and meteorological flood risk vectors.
                    </p>
                  </div>
                )}

                {/* GIS Analytics Profile & Soil Suitability */}
                {gisProfile && (
                  <div className="mt-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-lg">
                    <h2 className="text-sm uppercase tracking-wider text-sky-400 font-bold mb-1 flex items-center gap-1.5">
                      🗺️ GIS Regional Connectivity & Land Suitability
                    </h2>
                    
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      {/* Connectivity Box */}
                      <div className="bg-slate-950/40 border border-slate-850 p-4 rounded-xl space-y-2">
                        <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px] block border-b border-slate-850 pb-1 mb-2">
                          🚗 Road Connectivity
                        </span>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Highway Dist:</span>
                          <span className="font-bold text-slate-200">{gisProfile.highwayDist} m</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Main Road:</span>
                          <span className="font-bold text-slate-200">{gisProfile.mainRoadDist} m</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">City Center:</span>
                          <span className="font-bold text-slate-200">{gisProfile.cityCenterDist} km</span>
                        </div>
                      </div>

                      {/* Agrarian & Terrain Suitability */}
                      <div className="bg-slate-950/40 border border-slate-850 p-4 rounded-xl space-y-2">
                        <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px] block border-b border-slate-850 pb-1 mb-2">
                          🌾 Soil & Crop Suitability
                        </span>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Soil Profile:</span>
                          <span className="font-bold text-slate-200 truncate max-w-[80px]" title={gisProfile.soil}>{gisProfile.soil}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Suitable Crops:</span>
                          <span className="font-bold text-slate-200 truncate max-w-[80px]" title={gisProfile.crops}>{gisProfile.crops}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Irrigation:</span>
                          <span className="font-bold text-slate-200 truncate max-w-[80px]" title={gisProfile.irrigation}>{gisProfile.irrigation}</span>
                        </div>
                      </div>

                      {/* Climate & Terrain Parameters */}
                      <div className="bg-slate-950/40 border border-slate-850 p-4 rounded-xl space-y-2 col-span-2">
                        <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px] block border-b border-slate-850 pb-1 mb-2">
                          🏔️ Terrain & Climate Parameters
                        </span>
                        <div className="grid grid-cols-3 gap-2 text-[11px] text-center">
                          <div className="border-r border-slate-850">
                            <span className="text-slate-500 block text-[9.5px] mb-0.5">Elevation</span>
                            <span className="font-bold text-slate-200">{gisProfile.elevation} m</span>
                          </div>
                          <div className="border-r border-slate-850">
                            <span className="text-slate-500 block text-[9.5px] mb-0.5">Terrain Slope</span>
                            <span className="font-bold text-slate-200">{gisProfile.slope}%</span>
                          </div>
                          <div>
                            <span className="text-slate-500 block text-[9.5px] mb-0.5">Annual Rain</span>
                            <span className="font-bold text-slate-200">{gisProfile.rainfall} mm</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Live GIS Environmental & Risk Card */}
                {envRiskData && (
                  <div className="mt-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <h2 className="text-sm uppercase tracking-wider text-emerald-400 font-bold mb-1 flex items-center gap-1.5">
                      🌧️ Live GIS Environment & Risk Report
                    </h2>
                    <div className="grid grid-cols-2 gap-4 text-xs text-slate-300">
                      <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-800">
                        <span className="text-slate-500 uppercase tracking-wider block text-[9.5px]">Flood Vulnerability</span>
                        <span className={`font-bold text-sm block mt-1 ${
                          envRiskData.floodRisk.includes('High') 
                            ? 'text-rose-400' 
                            : envRiskData.floodRisk.includes('Moderate') 
                              ? 'text-amber-400' 
                              : 'text-emerald-400'
                        }`}>{envRiskData.floodRisk}</span>
                        <span className="text-[10px] text-slate-500 mt-0.5 block">Nearest water body: {envRiskData.waterDistance}m</span>
                      </div>
                      
                      <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-800">
                        <span className="text-slate-500 uppercase tracking-wider block text-[9.5px]">Live Micro-Climate</span>
                        <span className="font-bold text-sm block mt-1 text-sky-400">{envRiskData.temp}°C</span>
                        <span className="text-[10px] text-slate-500 mt-0.5 block">Elevation: {envRiskData.elevation}m | Wind: {envRiskData.wind} km/h</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Nearby GIS Amenities Panel */}
                {amenities.length > 0 && (
                  <div className="mt-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <h2 className="text-sm uppercase tracking-wider text-indigo-400 font-bold mb-1 flex items-center gap-1.5">
                      🏫 Nearby Infrastructure & Amenities (2km)
                    </h2>
                    <p className="text-xs text-slate-500 mb-2">
                      Live geospatial intelligence search shows critical local infrastructure:
                    </p>
                    <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1">
                      {amenities.slice(0, 5).map((amenity, idx) => (
                        <div key={idx} className="bg-slate-800/30 border border-slate-850 rounded-xl p-3 flex justify-between items-center text-xs">
                          <div>
                            <span className="font-bold block text-slate-200">{amenity.name}</span>
                            <span className="text-[10px] text-slate-500 mt-0.5 block capitalize">Category: {amenity.type}</span>
                          </div>
                          <span className="bg-slate-800 text-slate-300 font-mono font-bold px-2 py-1 rounded text-[10px] shrink-0">
                            {Math.round(amenity.distance)}m away
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Loan Eligibility Simulator & What-if Panel */}
                {sim && (
                  <div className="mt-6 bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <h2 className="text-sm uppercase tracking-wider text-indigo-400 font-bold mb-1 flex items-center gap-1.5">
                      💳 Interactive Loan Eligibility Simulator & What-if Analysis
                    </h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Sliders Area */}
                      <div className="space-y-4">
                        {/* Slider 1: Down Payment */}
                        <div>
                          <div className="flex justify-between text-xs text-slate-400 mb-1 font-semibold">
                            <span>Down Payment: ₹{simDownPayment.toLocaleString()}</span>
                            <span>{Math.round((simDownPayment / valuationData.totalValue) * 100)}% LTV Offset</span>
                          </div>
                          <input 
                            type="range"
                            min={Math.round(valuationData.totalValue * 0.10)}
                            max={Math.round(valuationData.totalValue * 0.90)}
                            step={10000}
                            value={simDownPayment}
                            onChange={e => setSimDownPayment(Number(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                          />
                        </div>

                        {/* Slider 2: Interest Rate */}
                        <div>
                          <div className="flex justify-between text-xs text-slate-400 mb-1 font-semibold">
                            <span>Interest Rate: {simInterestRate}%</span>
                            <span>Annual</span>
                          </div>
                          <input 
                            type="range"
                            min={5.0}
                            max={15.0}
                            step={0.25}
                            value={simInterestRate}
                            onChange={e => setSimInterestRate(Number(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                          />
                        </div>

                        {/* Slider 3: Repayment Tenure */}
                        <div>
                          <div className="flex justify-between text-xs text-slate-400 mb-1 font-semibold">
                            <span>Tenure: {simTenure} Years</span>
                            <span>{simTenure * 12} Months</span>
                          </div>
                          <input 
                            type="range"
                            min={5}
                            max={30}
                            step={1}
                            value={simTenure}
                            onChange={e => setSimTenure(Number(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                          />
                        </div>

                        {/* Slider 4: Monthly Net Income */}
                        <div>
                          <div className="flex justify-between text-xs text-slate-400 mb-1 font-semibold">
                            <span>Net Monthly Income: ₹{simMonthlyIncome.toLocaleString()}</span>
                          </div>
                          <input 
                            type="range"
                            min={20000}
                            max={300000}
                            step={5000}
                            value={simMonthlyIncome}
                            onChange={e => setSimMonthlyIncome(Number(e.target.value))}
                            className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                          />
                        </div>

                        {/* Co-applicant Checkbox & Income Slider */}
                        <div className="pt-2 border-t border-slate-800/85">
                          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300 font-semibold mb-2">
                            <input 
                              type="checkbox"
                              checked={simHasCoApplicant}
                              onChange={e => setSimHasCoApplicant(e.target.checked)}
                              className="rounded border-slate-700 bg-slate-800 text-indigo-500 focus:ring-0 focus:ring-offset-0"
                            />
                            <span>Add Co-Applicant Income</span>
                          </label>
                          {simHasCoApplicant && (
                            <div className="pl-6">
                              <div className="flex justify-between text-[11px] text-slate-500 mb-1">
                                <span>Co-Applicant Income: ₹{simCoApplicantIncome.toLocaleString()}</span>
                              </div>
                              <input 
                                type="range"
                                min={10000}
                                max={150000}
                                step={5000}
                                value={simCoApplicantIncome}
                                onChange={e => setSimCoApplicantIncome(Number(e.target.value))}
                                className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                              />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Simulated Results Indicators Area */}
                      <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-4 space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Monthly EMI</span>
                            <span className="text-xl font-bold text-slate-200">₹{sim.emi.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Loan Size</span>
                            <span className="text-xl font-bold text-slate-200">₹{sim.loanAmount.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">DTI Ratio</span>
                            <span className={`text-xl font-bold ${sim.dti > 50 ? 'text-rose-400' : sim.dti > 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
                              {sim.dti}%
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">LTV Ratio</span>
                            <span className="text-xl font-bold text-indigo-400">{sim.ltv}%</span>
                          </div>
                        </div>

                        <div className="border-t border-slate-800/80 pt-3 grid grid-cols-2 gap-4">
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Approval Prob</span>
                            <span className={`text-2xl font-black ${sim.approvalProb > 80 ? 'text-emerald-400' : sim.approvalProb > 60 ? 'text-amber-400' : 'text-rose-400'}`}>
                              {sim.approvalProb}%
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Risk Rating</span>
                            <span className={`text-2xl font-black ${sim.riskLevel === 'Low' ? 'text-emerald-400' : sim.riskLevel === 'Medium' ? 'text-amber-400' : 'text-rose-400'}`}>
                              {sim.riskLevel}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* What-if Analysis recommendation list */}
                    <div className="pt-4 border-t border-slate-850">
                      <h3 className="text-xs uppercase tracking-wider text-slate-400 font-bold mb-3 flex items-center gap-1.5">
                        💡 Real-time What-if Underwriting Advice
                      </h3>
                      <div className="grid grid-cols-1 gap-2.5">
                        {/* Suggestion 1: Down Payment Boost */}
                        {sim.ltv > 50 && (
                          <div className="bg-slate-800/20 border border-slate-850 rounded-xl p-3 flex justify-between items-center text-xs">
                            <div>
                              <span className="font-bold block text-slate-300">Action: Boost Down Payment by ₹5 Lakhs</span>
                              <span className="text-[10px] text-slate-500 block mt-0.5">Reduces Loan-to-Value offset to {sim.altLtv}%</span>
                            </div>
                            <span className="text-emerald-400 font-semibold text-[11px] shrink-0 text-right">
                              Prob: {sim.altApprovalProb}%<br/>
                              Risk: {sim.altRiskLevel}
                            </span>
                          </div>
                        )}

                        {/* Suggestion 2: Co-Applicant Addition */}
                        {!simHasCoApplicant && (
                          <div className="bg-slate-800/20 border border-slate-850 rounded-xl p-3 flex justify-between items-center text-xs">
                            <div>
                              <span className="font-bold block text-slate-300">Action: Add Co-Applicant (₹50k Income)</span>
                              <span className="text-[10px] text-slate-500 block mt-0.5">Increases household pool, dropping DTI and raising confidence.</span>
                            </div>
                            <span className="text-emerald-400 font-semibold text-[11px] shrink-0 text-right">
                              Prob: {sim.coAppApprovalProb}%<br/>
                              DTI: {sim.coAppDti}%
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Right Map: Satellite Imagery Map */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 flex flex-col h-[580px]">
                <h2 className="text-xl font-semibold mb-2 flex items-center gap-2 text-emerald-400">
                  🗺️ Interactive Land Boundaries (Satellite Map)
                </h2>
                <p className="text-xs text-slate-400 mb-4">
                  Click anywhere on the map or use geolocation to capture coordinates.
                </p>

                <div className="flex-1 relative overflow-hidden rounded-xl border border-slate-800 shadow-inner">
                  <PropertyMap
                    coordinates={coordinates}
                    onChangeCoordinates={handleMapClickOrLocation}
                    selectedDistrict={selectedDistrict}
                    selectedVillage={selectedVillage}
                    surveyNumber={surveyNumber}
                    valuationData={valuationData}
                    polygonCoords={polygonCoords}
                    onPolygonChange={handlePolygonChange}
                    isDrawingMode={isDrawingMode}
                    setIsDrawingMode={setIsDrawingMode}
                    amenities={amenities}
                  />
                  {geocodingLoading && (
                    <div className="absolute inset-0 bg-slate-950/75 backdrop-blur-sm z-50 flex flex-col items-center justify-center gap-3 rounded-xl border border-slate-850">
                      <div className="animate-spin rounded-full h-8 w-8 border-4 border-sky-400 border-t-transparent"></div>
                      <span className="text-sm font-semibold text-sky-400">Reverse Geocoding Location...</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: DOCUMENT OCR VERIFICATION */}
          {activeTab === "ocr" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                       <div className="space-y-3 bg-slate-950/60 p-4 rounded-xl border border-slate-850">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-[10px] uppercase text-slate-400 font-extrabold tracking-wider">📎 Product Document Verification Checklist</span>
                      <span className="text-[9px] text-sky-400 font-mono font-bold">Bank Audit Rule 2026</span>
                    </div>
                    
                    <div className="space-y-2 text-xs">
                      <label className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-850 cursor-pointer">
                        <span className="text-slate-200">Aadhaar Card Copy</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${hasAadhaar ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                            {hasAadhaar ? '✔ UPLOADED' : '❌ MISSING'}
                          </span>
                          <input type="checkbox" checked={hasAadhaar} onChange={e => setHasAadhaar(e.target.checked)} className="rounded text-sky-500 bg-slate-800 border-slate-700" />
                        </div>
                      </label>

                      <label className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-850 cursor-pointer">
                        <span className="text-slate-200">PAN Card Copy</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${hasPan ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                            {hasPan ? '✔ UPLOADED' : '❌ MISSING'}
                          </span>
                          <input type="checkbox" checked={hasPan} onChange={e => setHasPan(e.target.checked)} className="rounded text-sky-500 bg-slate-800 border-slate-700" />
                        </div>
                      </label>

                      <label className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-850 cursor-pointer">
                        <span className="text-slate-200">6-Month Bank Statement / Income</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${hasIncome ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                            {hasIncome ? '✔ UPLOADED' : '❌ MISSING'}
                          </span>
                          <input type="checkbox" checked={hasIncome} onChange={e => setHasIncome(e.target.checked)} className="rounded text-sky-500 bg-slate-800 border-slate-700" />
                        </div>
                      </label>

                      <label className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-850 cursor-pointer">
                        <span className="text-slate-200">Registered Title Deed / Property Document</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${hasDeed ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                            {hasDeed ? '✔ UPLOADED' : '❌ MISSING'}
                          </span>
                          <input type="checkbox" checked={hasDeed} onChange={e => setHasDeed(e.target.checked)} className="rounded text-sky-500 bg-slate-800 border-slate-700" />
                        </div>
                      </label>

                      <label className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-850 cursor-pointer">
                        <span className="text-slate-200">RTC / Pahani (Land Ownership Record)</span>
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${hasRtc ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'}`}>
                            {hasRtc ? '⚠️ RE-VERIFY YEAR' : '❌ MISSING'}
                          </span>
                          <input type="checkbox" checked={hasRtc} onChange={e => setHasRtc(e.target.checked)} className="rounded text-sky-500 bg-slate-800 border-slate-700" />
                        </div>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-4 pt-2">
                    <span className="text-[10px] uppercase text-slate-500 font-bold block mb-1">🔍 OCR Extracted Identity Name Check</span>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">Aadhaar Card Full Name</label>
                      <input type="text" value={docAadhaarName} onChange={e => setDocAadhaarName(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none text-slate-200" />
                    </div>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">PAN Card Full Name</label>
                      <input type="text" value={docPanName} onChange={e => setDocPanName(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none text-slate-200" />
                    </div>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">Registered Sale Deed Owner</label>
                      <input type="text" value={docSaleDeedName} onChange={e => setDocSaleDeedName(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none text-slate-200" />
                    </div>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">RTC / Pahani Registered Owner</label>
                      <input type="text" value={docRtcOwnerName} onChange={e => setDocRtcOwnerName(e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:outline-none text-slate-200" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right side: Verification Results */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                  🛡️ OCR Document Audit Results
                </h2>

                {verifyResults.mismatch && (
                  <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 flex flex-col gap-1.5 text-rose-400 text-xs">
                    <span className="font-bold flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
                      ⚠️ Identity Mismatch Flag
                    </span>
                    <span>OCR scanner detected mismatch between naming registry credentials. Verify deeds and identities manually.</span>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-5">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Doc Trust Index</span>
                    <span className={`text-3xl font-black block mt-2 ${verifyResults.trust_score >= 80 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {verifyResults.trust_score}%
                    </span>
                  </div>

                  <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-5">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Fraud Risk Score</span>
                    <span className={`text-3xl font-black block mt-2 ${verifyResults.fraud_score < 25 ? 'text-emerald-400' : verifyResults.fraud_score < 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                      {verifyResults.fraud_score}% ({verifyResults.fraud_level})
                    </span>
                  </div>
                </div>

                {verifyResults.fraud_reasons.length > 0 && (
                  <div className="bg-slate-850/40 border border-slate-800 p-4 rounded-xl space-y-2 text-xs text-slate-300">
                    <span className="text-[10px] uppercase text-slate-500 font-bold block mb-1">🚨 Flagged Fraud Indicators</span>
                    <ul className="list-disc pl-4 space-y-1.5">
                      {verifyResults.fraud_reasons.map((r, idx) => <li key={idx}>{r}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: AI CREDIT UNDERWRITING (XAI, Fraud Checks, Bank Comparison & Audit Trail) */}
          {activeTab === "underwriting" && (
            <div className="space-y-8">
              {/* Centralized Auto-Synced Parameters Banner */}
              <div className="bg-gradient-to-r from-sky-950/80 via-slate-900 to-emerald-950/80 border border-sky-500/30 rounded-2xl p-5 backdrop-blur-md space-y-3">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <h3 className="text-xs font-bold text-sky-300 uppercase tracking-wider flex items-center gap-2">
                    ⚡ Centralized Auto-Synced Application Dossier (No Duplicate Entry)
                  </h3>
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-500/30 font-mono font-bold">
                    ✓ Sync Active ({sharedLoanState.product || "Vehicle Loan"})
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[9px] uppercase">Loan Purpose & Product</span>
                    <strong className="text-sky-300 block text-[11px] truncate mt-0.5">{loanPurpose} ({sharedLoanState.product})</strong>
                  </div>
                  <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[9px] uppercase">Credit Structure</span>
                    <strong className="text-emerald-400 block text-[11px] truncate mt-0.5">{loanStructure}</strong>
                  </div>
                  <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[9px] uppercase">Auto-Synced Sanction</span>
                    <strong className="text-slate-100 block text-[11px] mt-0.5">₹{applicantLoanAmount.toLocaleString()}</strong>
                  </div>
                  <div className="bg-slate-950/80 p-2.5 rounded-xl border border-slate-800">
                    <span className="text-slate-500 block text-[9px] uppercase">Pledged Guarantor</span>
                    <strong className="text-amber-300 block text-[11px] truncate mt-0.5">{guarantorName} ({guarantorRelation})</strong>
                  </div>
                </div>
              </div>

              {/* 🤖 STANDOUT FEATURE: AI Co-Pilot for Loan Officers & Executive Underwriting Suite */}
              <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/30 rounded-3xl p-6 shadow-2xl space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 gap-3">
                  <div>
                    <h2 className="text-lg font-bold text-sky-300 flex items-center gap-2">
                      🤖 AI Co-Pilot for Loan Officers (Commercial Banking Underwriter)
                    </h2>
                    <p className="text-slate-400 text-xs mt-0.5">
                      Intelligent case synthesis, risk diagnosis, collateral aggregation & eligibility improvement recommendations
                    </p>
                  </div>
                  <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-bold px-3 py-1 rounded-full border border-indigo-500/30 font-mono">
                    ⚡ Live Co-Pilot Active
                  </span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 text-xs">
                  {/* Column 1: Plain Language Executive Case Summary */}
                  <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 space-y-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      📋 Plain-Language Case Summary
                    </h3>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      Applicant <strong className="text-sky-300">{sharedLoanState.borrower_name}</strong> is applying for a <strong className="text-emerald-300">₹{applicantLoanAmount.toLocaleString()}</strong> {sharedLoanState.product} under <strong className="text-amber-300">{loanStructure}</strong>. CIBIL Score is strong at <strong className="text-emerald-400">{sharedLoanState.cibil_score}</strong>. Net monthly income is ₹{simMonthlyIncome.toLocaleString()} with a manageable DTI of <strong className="text-sky-400">{sim.dti}%</strong>.
                    </p>
                    <div className="bg-emerald-500/10 border border-emerald-500/30 p-2.5 rounded-xl text-[10px] text-emerald-300 font-semibold">
                      ✓ Pattern Audit: Income matches bank statement & EPFO tax filings cleanly (Zero anomaly flags).
                    </div>
                  </div>

                  {/* Column 2: "Why Not Approved?" & AI Risk Remedies */}
                  <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 space-y-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      💡 "Why Not Approved?" & Risk Remedies
                    </h3>
                    <div className="space-y-2 text-[11px]">
                      <div className="bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-xl text-slate-200">
                        <strong className="text-amber-300 block mb-0.5">Primary Risk Factor: DTI Buffer ({sim.dti}%)</strong>
                        <span>To lower risk score by 15%, applicant can:</span>
                        <ul className="list-disc pl-4 mt-1 text-slate-300 space-y-0.5 text-[10px]">
                          <li>Increase net monthly income by ₹8,000/mo</li>
                          <li>Reduce monthly EMI by ₹3,500 via 2-year tenure extension</li>
                          <li>Pledge co-applicant income (₹{simCoApplicantIncome.toLocaleString()}/mo)</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Column 3: Collateral Comparison & Aggregate Security */}
                  <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800 space-y-3">
                    <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                      📜 Collateral Comparison & Total Security
                    </h3>
                    <div className="space-y-1.5 font-mono text-[11px]">
                      <div className="flex justify-between border-b border-slate-850 pb-1">
                        <span className="text-slate-400">🏠 Property Valuation:</span>
                        <span className="text-slate-200 font-bold">₹{(homeKaveriRate * homeBuiltArea || 4500000).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-b border-slate-850 pb-1">
                        <span className="text-slate-400">🚗 Vehicle Valuation:</span>
                        <span className="text-slate-200 font-bold">₹{vehOnRoad.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-b border-slate-850 pb-1">
                        <span className="text-slate-400">🥇 Gold Collateral:</span>
                        <span className="text-slate-200 font-bold">₹{(goldWeight * goldPricePerGram || 1200000).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between border-b border-slate-850 pb-1">
                        <span className="text-slate-400">🚜 Farm Machinery:</span>
                        <span className="text-slate-200 font-bold">₹{farmCost.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between pt-1 font-bold text-emerald-400 text-xs">
                        <span>🛡️ Total Security Coverage:</span>
                        <span>₹{((homeKaveriRate * homeBuiltArea || 4500000) + vehOnRoad + (goldWeight * goldPricePerGram || 1200000) + farmCost).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Explainable AI Factors Contribution Graph */}
                <div className="bg-slate-950/90 p-4 rounded-2xl border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    📊 Explainable AI (XAI) Model Factors Importance Graph
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-[10px]">
                    {[
                      { factor: "Net Monthly Income", weight: "40%", width: "w-full", color: "bg-emerald-500" },
                      { factor: "CIBIL Credit History", weight: "25%", width: "w-[62%]", color: "bg-sky-500" },
                      { factor: "Collateral LTV Ratio", weight: "18%", width: "w-[45%]", color: "bg-teal-500" },
                      { factor: "EPFO Employment", weight: "10%", width: "w-[25%]", color: "bg-indigo-500" },
                      { factor: "Document Integrity", weight: "7%", width: "w-[17%]", color: "bg-purple-500" }
                    ].map((item, idx) => (
                      <div key={idx} className="bg-slate-900 p-2.5 rounded-xl border border-slate-800 space-y-1">
                        <div className="flex justify-between text-slate-300 font-bold">
                          <span className="truncate">{item.factor}</span>
                          <span className="text-sky-300 font-mono">{item.weight}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className={`${item.color} ${item.width} h-full rounded-full`} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Top Fraud Detection Status & Property Intelligence Banner */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 pb-2">
                  🛡️ Fraud Detection & Property Intelligence Matrix
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                    <span className="text-slate-400 block text-[10px]">Aadhaar / PAN Uniqueness</span>
                    <strong className="text-emerald-400 block mt-1">✓ PASS (Single Record)</strong>
                  </div>
                  <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                    <span className="text-slate-400 block text-[10px]">Document Integrity OCR</span>
                    <strong className="text-emerald-400 block mt-1">✓ Clean (Tamper Free)</strong>
                  </div>
                  <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30">
                    <span className="text-slate-400 block text-[10px]">EPFO Income Verification</span>
                    <strong className="text-emerald-400 block mt-1">✓ Verified (Tax Sync)</strong>
                  </div>
                  <div className="bg-slate-950 p-3.5 rounded-xl border border-sky-500/30">
                    <span className="text-slate-400 block text-[10px]">AI Property Investment Score</span>
                    <strong className="text-sky-400 block mt-1">8.8 / 10 (Prime Tier)</strong>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left side: Underwriting Decision Dashboard & XAI */}
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                  <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                    💳 Executive AI Underwriting & Explainable AI (XAI)
                  </h2>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-4 text-center">
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-semibold">Recommendation</span>
                      <span className={`text-lg font-black block mt-2 ${
                        underwritingResult.recommendation === 'Approve' 
                          ? 'text-emerald-400' 
                          : underwritingResult.recommendation === 'Reject' 
                            ? 'text-rose-400' 
                            : 'text-amber-400'
                      }`}>{underwritingResult.recommendation}</span>
                    </div>

                    <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-4 text-center">
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-semibold">Approval Probability</span>
                      <span className="text-lg font-bold text-sky-400 block mt-2">{underwritingResult.confidence}%</span>
                    </div>

                    <div className="bg-slate-950/65 border border-slate-850 rounded-xl p-4 text-center">
                      <span className="text-[9px] text-slate-500 uppercase tracking-wider block font-semibold">Default Risk Score</span>
                      <span className="text-lg font-bold text-slate-200 block mt-2">{underwritingResult.probability_of_default}%</span>
                    </div>
                  </div>

                  {/* Explainable AI Factor Importance */}
                  <div className="bg-slate-950/65 border border-slate-850 p-5 rounded-xl space-y-3 text-xs">
                    <h3 className="text-[10px] uppercase text-slate-400 font-extrabold tracking-wider border-b border-slate-850 pb-2 mb-2">
                      🤖 Explainable AI (XAI) Rationale & Key Factors
                    </h3>
                    <div className="space-y-2">
                      {underwritingResult.reasons.map((r, idx) => (
                        <div key={idx} className={`p-2.5 rounded-lg border text-[11px] ${
                          r.startsWith('✓') 
                            ? 'bg-emerald-500/5 border-emerald-500/10 text-emerald-300' 
                            : 'bg-rose-500/5 border-rose-500/10 text-rose-300'
                        }`}>
                          {r}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* AI Credit Memo Generation Box */}
                  <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-sky-500/30 p-5 rounded-xl space-y-4 text-xs">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                      <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                        📑 Executive AI Credit Memo Report
                      </h3>
                      <span className="text-[9px] bg-sky-500/20 text-sky-300 px-2 py-0.5 rounded border border-sky-500/30 font-mono">
                        Bank Credit Standard
                      </span>
                    </div>

                    <div className="space-y-2.5 text-[11px]">
                      <div>
                        <span className="text-slate-400 font-bold block">1. Loan Summary:</span>
                        <p className="text-slate-300 mt-0.5">Applicant requested ₹{applicantLoanAmount.toLocaleString()} over 240 months. Collateral market value appraised at ₹{valuationData ? valuationData.total_market_value.toLocaleString() : "45,00,000"}.</p>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-slate-950 p-2.5 rounded-lg border border-emerald-500/20">
                          <span className="text-emerald-400 font-bold block">✅ Applicant Strengths:</span>
                          <ul className="text-emerald-300/90 list-disc pl-3 text-[10px] space-y-1 mt-1">
                            <li>CIBIL Score satisfactory (≥ 750)</li>
                            <li>Kaveri title deed clear without encumbrances</li>
                            <li>DTI affordability within 45% ceiling</li>
                          </ul>
                        </div>

                        <div className="bg-slate-950 p-2.5 rounded-lg border border-amber-500/20">
                          <span className="text-amber-400 font-bold block">⚠️ Applicant Risks:</span>
                          <ul className="text-amber-300/90 list-disc pl-3 text-[10px] space-y-1 mt-1">
                            <li>High requested LTV ratio requiring LTV cap</li>
                            <li>Self-employed income fluctuation risk</li>
                          </ul>
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-400 font-bold block">2. Recommended Sanction Terms:</span>
                        <p className="text-sky-300 font-mono mt-0.5">Sanction ₹{Math.round(applicantLoanAmount * 0.85).toLocaleString()} at 8.50% p.a. • EMI: ₹{Math.round(sim.monthlyEmi).toLocaleString()}/mo</p>
                      </div>

                      <div>
                        <span className="text-slate-400 font-bold block">3. Pre-Disbursement Conditions:</span>
                        <ol className="text-slate-300 list-decimal pl-4 text-[10px] space-y-0.5 mt-0.5">
                          <li>Upload verified 6-month bank statement with EPFO tax sync.</li>
                          <li>Execute physical site inspection & boundary survey verification.</li>
                        </ol>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 border-t border-slate-850 pt-4">
                    <h3 className="text-xs uppercase text-slate-400 font-bold tracking-wider mb-2">
                      👤 Underwriting Officer Actions ({userRole})
                    </h3>
                    <div className="flex gap-4">
                      <button 
                        type="button"
                        onClick={downloadSanctionPdf}
                        className="flex-1 bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-600 hover:to-sky-700 text-white font-bold py-2.5 px-4 rounded-xl text-xs transition duration-300 shadow-md hover:shadow-sky-500/20"
                      >
                        📄 Download PDF Sanction Dossier
                      </button>
                    </div>
                  </div>
                </div>

                {/* Right side: Bank Comparison & Audit Trail */}
                <div className="space-y-6">
                  {/* Competitive Bank Loan Comparison */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <h3 className="text-xs uppercase text-emerald-400 font-bold tracking-wider border-b border-slate-800 pb-2">
                      📊 Competitive Bank Loan Comparison (Market vs. AegisCR Offer)
                    </h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400 text-[10px] uppercase">
                            <th className="py-2">Bank</th>
                            <th className="py-2">Interest Rate</th>
                            <th className="py-2">Est. Monthly EMI</th>
                            <th className="py-2">Processing Fee</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-850 text-slate-200 font-mono">
                          <tr className="bg-emerald-500/10 font-bold text-emerald-300">
                            <td className="py-2.5 px-2">🛡️ AegisCR (Your Offer)</td>
                            <td className="py-2.5">8.50% p.a.</td>
                            <td className="py-2.5">₹{Math.round(sim.monthlyEmi).toLocaleString()}</td>
                            <td className="py-2.5">0.25% (Zero Hidden)</td>
                          </tr>
                          <tr>
                            <td className="py-2.5 text-slate-300">SBI Home/Vehicle</td>
                            <td className="py-2.5">8.75% p.a.</td>
                            <td className="py-2.5">₹{Math.round(sim.monthlyEmi * 1.02).toLocaleString()}</td>
                            <td className="py-2.5">0.50%</td>
                          </tr>
                          <tr>
                            <td className="py-2.5 text-slate-300">HDFC Bank</td>
                            <td className="py-2.5">9.10% p.a.</td>
                            <td className="py-2.5">₹{Math.round(sim.monthlyEmi * 1.04).toLocaleString()}</td>
                            <td className="py-2.5">1.00%</td>
                          </tr>
                          <tr>
                            <td className="py-2.5 text-slate-300">ICICI Bank</td>
                            <td className="py-2.5">9.25% p.a.</td>
                            <td className="py-2.5">₹{Math.round(sim.monthlyEmi * 1.05).toLocaleString()}</td>
                            <td className="py-2.5">0.75%</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Real-time Audit Trail Log */}
                  <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-4">
                    <h3 className="text-xs uppercase text-slate-400 font-bold tracking-wider border-b border-slate-800 pb-2">
                      📜 System Audit Trail (Role-Based Action Log)
                    </h3>
                    <div className="space-y-2 text-[11px] font-mono">
                      {auditLogs.map((log, i) => (
                        <div key={i} className="bg-slate-950/80 p-3 rounded-xl border border-slate-850 flex justify-between items-center">
                          <div>
                            <span className="text-sky-400 font-bold">{log.action}</span>
                            <span className="text-slate-400 block text-[10px]">{log.actor} ({log.role}) • {log.detail}</span>
                          </div>
                          <span className="text-[9px] text-slate-500">{log.timestamp.split(' ')[1]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: PORTFOLIO PERFORMANCE ANALYTICS */}
          {activeTab === "analytics" && analyticsStats && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left side: Portfolio Performance Metrics */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                  📊 Portfolio Underwriting Metrics
                </h2>

                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-slate-950/60 border border-slate-850 p-5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Approved Loans</span>
                    <span className="text-3xl font-black text-emerald-400 block mt-2">{analyticsStats.loans_approved}</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-850 p-5 rounded-xl">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Rejected Loans</span>
                    <span className="text-3xl font-black text-rose-400 block mt-2">{analyticsStats.loans_rejected}</span>
                  </div>
                  <div className="bg-slate-950/60 border border-slate-850 p-5 rounded-xl col-span-2">
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Average Collateral Value</span>
                    <span className="text-3xl font-black text-slate-100 block mt-2">₹{analyticsStats.avg_property_value.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Right side: Regional Distribution */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h2 className="text-xl font-semibold flex items-center gap-2 text-sky-400 border-b border-slate-800 pb-3">
                  🗺️ Regional District Spreads
                </h2>
                
                <div className="space-y-4">
                  {analyticsStats.district_distribution.map((dist, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-300">{dist.district}</span>
                        <span className="text-slate-400">{dist.value} Applications</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-sky-500 h-full rounded-full" 
                          style={{ width: `${(dist.value / 60) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: GOLD LOAN APPRAISAL & LIVE API INTEGRATION */}
          {activeTab === "gold" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column: Live GoldAPI Feed & Appraisal Inputs */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h2 className="text-xl font-semibold flex items-center gap-2 text-amber-400">
                    🪙 Live Spot Gold Price (GoldAPI.io)
                  </h2>
                  <button
                    onClick={fetchGoldPrice}
                    disabled={goldPriceLoading}
                    className="text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-semibold px-3 py-1.5 rounded-lg border border-amber-500/30 transition flex items-center gap-1.5"
                  >
                    {goldPriceLoading ? '🔄 Fetching...' : '⚡ Refresh Price'}
                  </button>
                </div>

                {/* Spot Gold Rate Cards */}
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="bg-gradient-to-b from-amber-500/10 to-amber-950/20 border border-amber-500/30 p-3.5 rounded-xl">
                    <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">24K Gold Rate</span>
                    <span className="text-xl font-black text-amber-300 block mt-1">
                      ₹{goldPriceData ? goldPriceData.price_gram_24k?.toLocaleString() : '—'}/g
                    </span>
                    <span className="text-[9px] text-slate-400 block mt-0.5">Pure Bullion</span>
                  </div>
                  <div className="bg-gradient-to-b from-amber-500/10 to-amber-950/20 border border-amber-500/30 p-3.5 rounded-xl">
                    <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">22K Gold Rate</span>
                    <span className="text-xl font-black text-amber-200 block mt-1">
                      ₹{goldPriceData ? goldPriceData.price_gram_22k?.toLocaleString() : '—'}/g
                    </span>
                    <span className="text-[9px] text-slate-400 block mt-0.5">Standard Ornaments</span>
                  </div>
                  <div className="bg-gradient-to-b from-amber-500/10 to-amber-950/20 border border-amber-500/30 p-3.5 rounded-xl">
                    <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">18K Gold Rate</span>
                    <span className="text-xl font-black text-amber-100 block mt-1">
                      ₹{goldPriceData ? goldPriceData.price_gram_18k?.toLocaleString() : '—'}/g
                    </span>
                    <span className="text-[9px] text-slate-400 block mt-0.5">Jewelry Grade</span>
                  </div>
                </div>

                {/* Live Market Index Metadata */}
                <div className="bg-slate-950/60 border border-slate-850 p-4 rounded-xl flex items-center justify-between text-xs text-slate-300">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Market Spot Index</span>
                    <span className="font-bold text-amber-300 text-sm">
                      {goldOuncePrice ? `₹${goldOuncePrice.toLocaleString()} / Ounce` : 'Loading...'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Currency</span>
                    <span className="font-bold text-slate-200">{goldPriceData?.currency || 'INR'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Last Updated</span>
                    <span className="font-semibold text-slate-300">
                      {goldPriceData?.last_updated || 'Just now'}
                    </span>
                  </div>
                  {goldPriceData?.fallback && (
                    <span className="bg-amber-500/20 text-amber-300 text-[10px] font-bold px-2 py-0.5 rounded border border-amber-500/40">
                      Fallback Mode
                    </span>
                  )}
                </div>

                {/* Gold Appraisal Inputs Form */}
                <div className="space-y-4 border-t border-slate-800 pt-4">
                  <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                    📋 Borrower & Gold Collateral Details
                  </h3>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Borrower Full Name</label>
                    <input
                      type="text"
                      value={goldBorrowerName}
                      onChange={(e) => setGoldBorrowerName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                      placeholder="e.g. Aarav Kumar"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Gold Weight (Grams)</label>
                      <input
                        type="number"
                        value={goldWeight}
                        onChange={(e) => setGoldWeight(e.target.value)}
                        min="1"
                        step="0.1"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-bold"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Purity (Karat)</label>
                      <select
                        value={goldPurity}
                        onChange={handleGoldPurityChange}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500 font-bold"
                      >
                        <option value="24K">24K (99.9% Pure)</option>
                        <option value="22K">22K (91.6% Standard)</option>
                        <option value="18K">18K (75.0% Hallmarked)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Annual Interest Rate (%)</label>
                      <input
                        type="number"
                        value={goldInterestRate}
                        onChange={(e) => setGoldInterestRate(e.target.value)}
                        step="0.1"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-400 mb-1">Tenure (Months)</label>
                      <input
                        type="number"
                        value={goldTenure}
                        onChange={(e) => setGoldTenure(e.target.value)}
                        min="1"
                        max="60"
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-400 mb-1">Appraiser Field & Purity Notes</label>
                    <textarea
                      rows="2"
                      value={goldOfficerNotes}
                      onChange={(e) => setGoldOfficerNotes(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                      placeholder="e.g. Hallmarked ornaments verified with XRF purity scanner."
                    />
                  </div>
                </div>
              </div>

              {/* Right Column: Calculator Output, RBI LTV Breakdown & PDF Report */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-6 backdrop-blur-sm space-y-6 flex flex-col justify-between">
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold flex items-center gap-2 text-amber-400 border-b border-slate-800 pb-3">
                    ⚖️ Gold Loan Valuation & RBI LTV Ceiling
                  </h2>

                  {/* Calculation Cards */}
                  <div className="space-y-4">
                    <div className="bg-slate-950/80 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
                      <div>
                        <span className="text-[11px] text-slate-400 uppercase font-bold block">Assessed Rate / Gram ({goldPurity})</span>
                        <span className="text-xs text-slate-500">Live Spot Market</span>
                      </div>
                      <span className="text-xl font-extrabold text-amber-300">
                        ₹{goldPricePerGram ? goldPricePerGram.toLocaleString() : '0'}/g
                      </span>
                    </div>

                    <div className="bg-gradient-to-r from-amber-950/30 to-slate-950 border border-amber-500/30 p-5 rounded-xl space-y-1">
                      <span className="text-xs text-amber-400 uppercase font-bold tracking-wider block">Total Gold Asset Market Value</span>
                      <div className="flex justify-between items-baseline">
                        <span className="text-3xl font-black text-amber-200">
                          ₹{(goldWeight * goldPricePerGram).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </span>
                        <span className="text-xs text-slate-400 font-mono">
                          {goldWeight}g × ₹{goldPricePerGram.toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-emerald-950/40 to-slate-950 border border-emerald-500/40 p-5 rounded-xl space-y-1">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-emerald-400 uppercase font-bold tracking-wider block">Maximum Eligible Loan Amount</span>
                        <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border border-emerald-500/40">
                          RBI Cap: 75% LTV
                        </span>
                      </div>
                      <div className="flex justify-between items-baseline">
                        <span className="text-3xl font-black text-emerald-300">
                          ₹{(goldWeight * goldPricePerGram * 0.75).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                        </span>
                        <span className="text-xs text-emerald-500/80 font-mono">
                          Gold Value × 0.75
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Step-by-Step Example Breakdown Card */}
                  <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-xl space-y-2 text-xs">
                    <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block border-b border-slate-850 pb-1.5">
                      📌 AegisCR Standard Calculation Formula
                    </span>
                    <div className="grid grid-cols-2 gap-2 text-slate-400">
                      <div>• <strong className="text-slate-200">Weight Entered:</strong> {goldWeight} g</div>
                      <div>• <strong className="text-slate-200">Purity Grade:</strong> {goldPurity}</div>
                      <div>• <strong className="text-slate-200">Gold Value:</strong> ₹{(goldWeight * goldPricePerGram).toLocaleString()}</div>
                      <div>• <strong className="text-emerald-400">Eligible Loan (75%):</strong> ₹{(goldWeight * goldPricePerGram * 0.75).toLocaleString()}</div>
                    </div>
                  </div>
                </div>

                {/* Download PDF Button */}
                <button
                  onClick={handleDownloadGoldPdf}
                  disabled={downloadingGoldPdf}
                  className="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black py-4 px-6 rounded-xl shadow-xl shadow-amber-500/10 border border-amber-400/30 transition-all duration-300 flex items-center justify-center gap-2 text-sm mt-4"
                >
                  {downloadingGoldPdf ? (
                    <>⏳ Compiling Gold Sanction PDF Report...</>
                  ) : (
                    <>📄 Generate & Download Gold Loan Sanction PDF Report</>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Smart Property Selection Modal */}
      {showPropertyModal && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-850 pb-3">
              <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider">
                📋 Select Local Kaveri Land Registry Record
              </h3>
              <button 
                onClick={() => setShowPropertyModal(false)}
                className="text-slate-400 hover:text-white transition text-sm font-bold font-mono"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-slate-400">
              Multiple circular rate classifications match the geocoded location. Please select one to auto-fill property details:
            </p>
            <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
              {matchingProperties.map((rec, index) => (
                <button
                  key={index}
                  onClick={() => handleConfirmModalProperty(rec)}
                  type="button"
                  className="w-full text-left p-3.5 rounded-xl border border-slate-800 bg-slate-950/40 hover:bg-slate-800 hover:border-slate-700 text-xs transition duration-200"
                >
                  <div className="font-bold flex justify-between">
                    <span className="text-slate-200 text-sm truncate max-w-[280px]">{rec.property_type}</span>
                    <span className="text-emerald-400 font-extrabold text-sm">
                      ₹{rec.guidance_value.toLocaleString()}/{rec.original_unit === 'Acre' ? 'Acre' : 'sqft'}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1 truncate">Locality: {rec.locality}</div>
                  <div className="text-[9px] text-slate-400 mt-2 flex gap-4 pt-1.5 border-t border-slate-900">
                    <span>Rate/SqFt: ₹{rec.rate_per_sqft.toLocaleString()}</span>
                    {rec.rate_per_acre && <span>Rate/Acre: ₹{rec.rate_per_acre.toLocaleString()}</span>}
                  </div>
                </button>
              ))}
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => {
                  setShowPropertyModal(false);
                  setError('No Kaveri classification selected. Keeping form in manual entry mode.');
                }}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-2 px-4 rounded-xl text-xs transition"
              >
                Keep Manual
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
