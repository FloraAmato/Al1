import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { disputesApi } from '@/api/disputes'

export default function DashboardPage() {
  const { data: disputes, isLoading } = useQuery({
    queryKey: ['disputes'],
    queryFn: disputesApi.list,
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link
          to="/disputes/create"
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Create New Dispute
        </Link>
      </div>

      {/* Statistics */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Disputes</h3>
          <p className="text-3xl font-bold">{disputes?.length || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Active</h3>
          <p className="text-3xl font-bold">
            {disputes?.filter((d) => d.status === 'bidding').length || 0}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Finalized</h3>
          <p className="text-3xl font-bold">
            {disputes?.filter((d) => d.status === 'finalized').length || 0}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Rejected</h3>
          <p className="text-3xl font-bold">
            {disputes?.filter((d) => d.status === 'rejected').length || 0}
          </p>
        </div>
      </div>

      {/* Recent Disputes */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Recent Disputes</h2>

          {isLoading ? (
            <p>Loading...</p>
          ) : disputes && disputes.length > 0 ? (
            <div className="space-y-2">
              {disputes.slice(0, 5).map((dispute) => (
                <Link
                  key={dispute.id}
                  to={`/disputes/${dispute.id}`}
                  className="block p-4 border rounded hover:bg-gray-50"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold">{dispute.name}</h3>
                      <p className="text-sm text-gray-500">
                        {dispute.agents?.length || 0} agents, {dispute.goods?.length || 0} goods
                      </p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        dispute.status === 'finalized'
                          ? 'bg-green-100 text-green-800'
                          : dispute.status === 'rejected'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {dispute.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No disputes yet. Create one to get started!</p>
          )}
        </div>
      </div>
    </div>
  )
}
