// ui-one/src/RecentSearches.tsx
interface RecentSearchesProps {
    searches: string[];
}

export function RecentSearches({ searches }: RecentSearchesProps) {
    return (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
            <h2 className="text-xl font-bold">Recent Searches</h2>
            <ul className="mt-2">
                {searches.map((search, index) => (
                    <li key={index} className="mb-1">{search}</li>
                ))}
            </ul>
        </div>
    );
}