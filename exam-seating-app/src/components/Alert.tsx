// components/Alert.tsx
import { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

function Alert({ children }: Props) {
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4 rounded">
      {children}
    </div>
  );
}

export default Alert;
