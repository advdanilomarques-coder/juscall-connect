import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Scale, Bell, MapPin, Clock, CheckCircle, XCircle } from "lucide-react";
import { Link } from "react-router-dom";

const MOCK_REQUESTS = [
  {
    id: 1,
    clientName: "Cliente Anônimo #4521",
    caseType: "Flagrante - Delegacia",
    distance: "2 km",
    time: "Agora",
    urgent: true,
  },
  {
    id: 2,
    clientName: "Cliente Anônimo #3892",
    caseType: "Violência Doméstica",
    distance: "0.5 km",
    time: "3 min atrás",
    urgent: true,
  },
  {
    id: 3,
    clientName: "Cliente Anônimo #7123",
    caseType: "Consulta Trabalhista",
    distance: "5 km",
    time: "15 min atrás",
    urgent: false,
  },
];

const LawyerDashboard = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [requests, setRequests] = useState(MOCK_REQUESTS);

  const handleAccept = (id: number) => {
    setRequests(requests.filter((r) => r.id !== id));
  };

  const handleReject = (id: number) => {
    setRequests(requests.filter((r) => r.id !== id));
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">
              <span className="text-primary">Jus</span>
              <span className="text-accent">Call</span>
            </h1>
            <Badge variant="secondary">Pro</Badge>
          </div>
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
        </div>
      </header>

      {/* Status Bar */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto p-4">
          <Card className={`p-4 ${isOnline ? "bg-accent/10 border-accent" : "bg-muted"}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`h-4 w-4 rounded-full ${isOnline ? "bg-accent animate-pulse" : "bg-muted-foreground"}`} />
                <div>
                  <p className="font-semibold">
                    Status: {isOnline ? "ONLINE (Plantão)" : "OFFLINE"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {isOnline ? "Você está recebendo chamados" : "Você não está recebendo chamados"}
                  </p>
                </div>
              </div>
              <Switch checked={isOnline} onCheckedChange={setIsOnline} />
            </div>
          </Card>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">Chamados Recentes</h2>
          <Badge variant="secondary">{requests.length} pendentes</Badge>
        </div>

        {requests.length === 0 ? (
          <Card className="p-8 text-center">
            <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Nenhum chamado pendente no momento</p>
            <p className="text-xs text-muted-foreground mt-2">
              {isOnline ? "Aguardando novos chamados..." : "Ative o plantão para receber chamados"}
            </p>
          </Card>
        ) : (
          <div className="space-y-3">
            {requests.map((request) => (
              <Card
                key={request.id}
                className={`p-4 ${request.urgent ? "border-emergency" : ""}`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">{request.clientName}</h3>
                        {request.urgent && (
                          <Badge variant="destructive" className="text-xs">Urgente</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{request.caseType}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          <span>{request.distance}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>{request.time}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link to="/connection" className="flex-1">
                      <Button
                        className="w-full bg-accent hover:bg-accent/90"
                        onClick={() => handleAccept(request.id)}
                      >
                        <CheckCircle className="h-4 w-4" />
                        Aceitar
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      onClick={() => handleReject(request.id)}
                    >
                      <XCircle className="h-4 w-4" />
                      Recusar
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Subscription Widget */}
        <Card className="p-6 bg-gradient-to-br from-secondary/10 to-secondary/5 border-secondary">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold mb-1">Plano JusCall Pro</h3>
              <p className="text-sm text-muted-foreground mb-2">Status: Ativo</p>
              <p className="text-xs text-muted-foreground">
                Acesso ilimitado a chamados e recursos premium
              </p>
            </div>
            <Badge variant="secondary">R$ 99/mês</Badge>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default LawyerDashboard;
