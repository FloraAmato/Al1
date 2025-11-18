import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Fair Division Made Simple
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
          CREA2 is a platform for solving fair division problems using advanced
          optimization algorithms. Create disputes, define agents and goods, and
          let our system find the optimal allocation.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/register"
            className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-lg font-semibold"
          >
            Get Started
          </Link>
          <Link
            to="/help"
            className="px-8 py-3 border-2 border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 text-lg font-semibold"
          >
            Learn More
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-8">
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-bold mb-3">Fair Allocation</h3>
          <p className="text-gray-600">
            Use proven optimization algorithms to ensure fair distribution of
            goods among participants.
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-bold mb-3">Easy to Use</h3>
          <p className="text-gray-600">
            Simple interface for defining disputes, agents, goods, and
            preferences.
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-bold mb-3">Blockchain Verified</h3>
          <p className="text-gray-600">
            Optional blockchain anchoring for tamper-proof verification of
            results.
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-12">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              1
            </div>
            <h4 className="font-semibold mb-2">Create Dispute</h4>
            <p className="text-sm text-gray-600">
              Define your fair division problem
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              2
            </div>
            <h4 className="font-semibold mb-2">Add Participants</h4>
            <p className="text-sm text-gray-600">Invite agents and define goods</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              3
            </div>
            <h4 className="font-semibold mb-2">Submit Preferences</h4>
            <p className="text-sm text-gray-600">
              Agents provide bids or ratings
            </p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
              4
            </div>
            <h4 className="font-semibold mb-2">Get Solution</h4>
            <p className="text-sm text-gray-600">
              Review and finalize fair allocation
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
