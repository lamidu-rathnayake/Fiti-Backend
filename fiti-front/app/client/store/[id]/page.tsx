import { ViewShell } from "@/components/ViewShell";
import { StoreDetailPage } from "@/components/StoreDetailPage";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function StoreDetailRoute({ params }: Props) {
  const { id } = await params;
  return (
    <ViewShell>
      <StoreDetailPage shopId={id} />
    </ViewShell>
  );
}
