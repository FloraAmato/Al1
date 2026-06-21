import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { disputesApi } from '@/api/disputes'

export default function DisputeCreatePage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    resolution_method: 'bids' as 'bids' | 'ratings',
    bounds_percentage: 0.25,
    rating_weight: 1.1,
  })

  const createMutation = useMutation({
    mutationFn: disputesApi.create,
    onSuccess: (data) => {
      navigate(`/disputes/${data.id}`)
    },
    onError: () => {
      alert('Failed to create dispute')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Create New Dispute</h1>

      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Dispute Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="e.g., Family Estate Division"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Resolution Method</label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="method"
                value="bids"
                checked={formData.resolution_method === 'bids'}
                onChange={() => setFormData({ ...formData, resolution_method: 'bids' })}
                className="mr-2"
              />
              <span>Bids (monetary values)</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="method"
                value="ratings"
                checked={formData.resolution_method === 'ratings'}
                onChange={() => setFormData({ ...formData, resolution_method: 'ratings' })}
                className="mr-2"
              />
              <span>Ratings (star ratings)</span>
            </label>
          </div>
        </div>

        {formData.resolution_method === 'bids' && (
          <div>
            <label className="block text-sm font-medium mb-2">
              Bounds Percentage (0-100%)
            </label>
            <input
              type="number"
              value={formData.bounds_percentage * 100}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  bounds_percentage: parseFloat(e.target.value) / 100,
                })
              }
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              min="0"
              max="100"
              step="1"
            />
            <p className="text-sm text-gray-500 mt-1">
              Allowed deviation from estimated value
            </p>
          </div>
        )}

        {formData.resolution_method === 'ratings' && (
          <div>
            <label className="block text-sm font-medium mb-2">
              Rating Weight (1.0-2.0)
            </label>
            <input
              type="number"
              value={formData.rating_weight}
              onChange={(e) =>
                setFormData({ ...formData, rating_weight: parseFloat(e.target.value) })
              }
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              min="1.0"
              max="2.0"
              step="0.1"
            />
            <p className="text-sm text-gray-500 mt-1">
              Weight factor for rating calculation
            </p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="flex-1 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Dispute'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/disputes')}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
