export default function PharmacySupport() {
  return (
    <div className="w-full min-h-screen bg-[#050505] flex flex-col">
      <iframe
        src="http://localhost:3001"
        className="w-full flex-1 border-0"
        title="Pharmacy Support System"
        allow="geolocation; microphone; camera"
      />
    </div>
  );
}
