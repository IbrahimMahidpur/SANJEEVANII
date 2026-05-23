import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Chat from './pages/Chat';
import PharmacySupport from './pages/PharmacySupport';
import PrescriptionAnalysis from './pages/PrescriptionAnalysis';
import Sanjeevani from './pages/Sanjeevani';
import OutbreakAlert from './pages/OutbreakAlert';
import CommunityForum from './pages/CommunityForum';
import CBT from '../CBT';

import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/sanjeevani" element={<Sanjeevani />} />
          <Route path="/pharmacy-support" element={<PharmacySupport />} />
          <Route path="/prescription-analysis" element={<PrescriptionAnalysis />} />
          <Route path="/outbreak-alerts" element={<OutbreakAlert />} />
          <Route path="/community-forum" element={<CommunityForum />} />
          <Route path="/cbt" element={<CBT />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
