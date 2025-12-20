import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ImageSource } from '../api/types';
import { getImages } from '../api/sourcesClient';
import { getConfidenceColor } from '../utils/styleUtils';

type SourceCardProps = {
  image: ImageSource;
  confidence?: number;
};

export const SourceCard: React.FC<SourceCardProps> = ({ image, confidence }) => {

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {image.image_url && (
        <img
          src={image.image_url}
          alt={image.name}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-semibold flex-1">{image.name}</h2>
          {confidence !== undefined && (
            <span
              className={`ml-2 px-2 py-1 rounded text-xs font-semibold border ${getConfidenceColor(
                confidence
              )}`}
            >
              {(confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <p className="text-gray-600 mb-2 line-clamp-3">{image.description}</p>
        <p className="text-sm text-gray-500 mb-4">
          {image.launch_date && new Date(image.launch_date).toLocaleDateString()}
        </p>
        {image.image_url && (
          <a
            href={image.image_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            View Full Image
          </a>
        )}
      </div>
    </div>
  );
};

const Sources: React.FC = () => {
  const {
    data: images,
    isLoading,
    isError,
  } = useQuery<ImageSource[], Error>({
    queryKey: ['sources'],
    queryFn: getImages,
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-16">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (isError) {
    return <div className="text-red-500 text-center py-8">Failed to fetch space images</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {images?.map((image: ImageSource) => (
        <SourceCard key={image.id} image={image} />
      ))}
    </div>
  );
};

export default Sources; 