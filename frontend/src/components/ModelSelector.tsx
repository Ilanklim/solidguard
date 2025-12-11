interface Props {
  model: string;
  onChange: (m: string) => void;
}

export function ModelSelector({ model, onChange }: Props) {
  return (
    <select
      value={model}
      onChange={(e) => onChange(e.target.value)}
      className="px-3 py-1 rounded bg-muted text-foreground border border-border"
    >
      <option value="gpt-4.1-mini">GPT-4.1-mini</option>
      <option value="gpt-4.1">GPT-4.1</option>
      <option value="gpt-5.1">GPT-5.1</option>
    </select>
  );
}
