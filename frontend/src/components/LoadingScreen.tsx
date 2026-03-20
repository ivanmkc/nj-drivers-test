export default function LoadingScreen() {
  return (
    <div className="text-center pt-[30vh] text-gray-400 text-lg">
      <div className="inline-block w-8 h-8 border-[3px] border-gray-200 border-t-blue-600 rounded-full spinner mb-4" />
      <div>Loading questions...</div>
    </div>
  )
}
