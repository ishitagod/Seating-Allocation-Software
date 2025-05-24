// components/Buttons.tsx
interface Props {
  label: string;
  onClick: () => void;
}

function Buttons({ label, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
    >
      {label}
    </button>
  );
}

export default Buttons;
