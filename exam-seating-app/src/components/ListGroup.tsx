// components/ListGroup.tsx
interface Props {
  items: string[];
}

function ListGroup({ items }: Props) {
  return (
    <ul className="list-disc list-inside">
      {items.map((item, index) => (
        <li key={index} className="my-1">
          {item}
        </li>
      ))}
    </ul>
  );
}

export default ListGroup;

//use like <ListGroup items={["Exam File uploaded", "Room File uploaded"]} />
