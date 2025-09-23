import { Button } from "@/components/ui/button"

export default function Navbar() {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b bg-white shadow-sm">
      <h1 className="text-xl font-bold">📊 SPAC Monitor</h1>
      <Button variant="outline">Log Out</Button>
    </header>
  )
}