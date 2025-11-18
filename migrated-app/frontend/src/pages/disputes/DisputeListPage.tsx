import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { disputesApi } from '@/api/disputes'

export default function DisputeListPage() {
  const { data: disputes, isLoading } = useQuery({
    queryKey: ['disputes'],
    queryFn: disputesApi.list,
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">My Disputes</h1>
        <Link
          to="/disputes/create"
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Create New Dispute
        </Link>
      </div>

      {isLoading ? (
        <p>Loading...</p>
      ) : disputes && disputes.length > 0 ? (
        <div className="grid gap-4">
          {disputes.map((dispute) => (
            <Link
              key={dispute.id}
              to={`/disputes/${dispute.id}`}
              className="block bg-white p-6 rounded-lg shadow hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold mb-2">{dispute.name}</h3>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>{dispute.agents?.length || 0} agents</span>
                    <span>{dispute.goods?.length || 0} goods</span>
                    <span>
                      Method: {dispute.resolution_method === 'bids' ? 'Bids' : 'Ratings'}
                    </span>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    dispute.status === 'finalized'
                      ? 'bg-green-100 text-green-800'
                      : dispute.status === 'rejected'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {dispute.status.replace('_', ' ')}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500 mb-4">No disputes yet</p>
          <Link
            to="/disputes/create"
            className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Create Your First Dispute
          </Link>
        </div>
      )}
    </div>
  )
}
