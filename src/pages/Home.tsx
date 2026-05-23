
import { Link } from 'react-router-dom';
import Orb from '../components/Orb';
import StaggeredMenu from '../components/StaggeredMenu';

const menuItems = [
  { label: 'Home', ariaLabel: 'Go to home page', link: '/' },
  { label: 'Chatbot', ariaLabel: 'Go to chatbot', link: '/chat' },
  { label: 'Sanjeevani', ariaLabel: 'AI Avatar Assistant', link: '/sanjeevani' },
  { label: 'Prescription Analysis', ariaLabel: 'Analyze prescriptions', link: '/prescription-analysis' },
  { label: 'Symptom Checker', ariaLabel: 'Check symptoms', link: '/symptom-checker' },
  { label: 'Outbreak Alerts', ariaLabel: 'View outbreak alerts', link: '/outbreak-alerts' },
  { label: 'Pharmacy Support', ariaLabel: 'Find pharmacies', link: '/pharmacy-support' },
  { label: 'Doctors Connect', ariaLabel: 'Connect with doctors', link: '/doctors-connect' },
  { label: 'Community Forum', ariaLabel: 'Join community', link: '/community-forum' },
  { label: 'Cognitive Behavioural Therapy', ariaLabel: 'CBT Module', link: '/cbt' }
];

const socialItems = [
  { label: 'Twitter', link: 'https://twitter.com' },
  { label: 'GitHub', link: 'https://github.com' },
  { label: 'LinkedIn', link: 'https://linkedin.com' }
];

export default function Home() {
  return (
    <div className="relative w-full min-h-screen bg-black text-white font-sans">
      <div className="fixed inset-0 z-30 pointer-events-none">
        <StaggeredMenu
          position="right"
          items={menuItems}
          socialItems={socialItems}
          displaySocials={true}
          displayItemNumbering={true}
          menuButtonColor="#fff"
          openMenuButtonColor="#000"
          changeMenuColorOnOpen={true}
          colors={['#B19EEF', '#5227FF']}
          logoUrl=""
          accentColor="#ff6b6b"
          onMenuOpen={() => console.log('Menu opened')}
          onMenuClose={() => console.log('Menu closed')}
          className="[&_.sm-logo]:hidden [&_.staggered-menu-panel]:pointer-events-auto"
        />
      </div>

      {/* Orb Background - Absolute (Scrolls with page) */}
      <div className="absolute top-0 left-0 w-full h-screen z-0 flex items-center justify-center">
        <div className="w-full h-full">
          <Orb hoverIntensity={0.5} rotateOnHover={true} hue={0} forceHoverState={false} />
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="relative z-10 pointer-events-none">
        {/* Page 1: Hero */}
        <section className="h-screen flex flex-col items-center justify-center text-center px-4">
          {/* Badge */}


          {/* Heading */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-white pointer-events-auto">
            This orb is hiding <br />
            something, try hovering!
          </h1>

          {/* Buttons */}
          <div className="flex items-center gap-4 pointer-events-auto">
            <Link
              to="/chat"
              className="px-8 py-3 rounded-full bg-white text-black font-medium hover:bg-gray-100 transition-colors"
            >
              Get Started
            </Link>
            <button className="px-8 py-3 rounded-full border border-gray-700 bg-gray-900/50 hover:bg-gray-800 transition-colors text-white font-medium">
              Learn More
            </button>
          </div>
        </section>

        {/* Page 2: Blank Section */}
        <section className="h-screen w-full">
          {/* Content for the second page goes here */}
        </section>
      </div>
    </div>
  );
}
