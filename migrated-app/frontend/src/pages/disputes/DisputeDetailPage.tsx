import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { disputesApi } from '@/api/disputes'

export default function DisputeDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: dispute, isLoading } = useQuery({
    queryKey: ['dispute', id],
    queryFn: () => disputesApi.get(id!),
  })

  if (isLoading) return <div>Loading...</div>
  if (!dispute) return <div>Dispute not found</div>

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{dispute.name}</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Dispute Details</h2>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="font-medium text-gray-500">Status</dt>
            <dd>{dispute.status}</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-500">Resolution Method</dt>
            <dd>{dispute.resolution_method}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
