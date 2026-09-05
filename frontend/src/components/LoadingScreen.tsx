export default function LoadingScreen() {
  return (
    <div className="text-center pt-[30vh] text-subtle text-lg">
      <div className="inline-block w-8 h-8 border-[3px] border-border border-t-primary rounded-full spinner mb-4" />
      <div>Loading questions...</div>
    </div>
  );
}
