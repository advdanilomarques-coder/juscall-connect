import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Scale, MapPin, Phone, AlertCircle, X } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Link } from "react-router-dom";

const MOCK_LAWYERS = [
  { id: 1, name: "Dr. João Silva", oab: "OAB/SP 123456", distance: "0.8 km", expertise: "Criminal", lat: -23.55, lng: -46.63 },
  { id: 2, name: "Dra. Maria Santos", oab: "OAB/SP 234567", distance: "1.2 km", expertise: "Família", lat: -23.56, lng: -46.64 },
  { id: 3, name: "Dr. Pedro Costa", oab: "OAB/RJ 345678", distance: "2.1 km", expertise: "Trabalhista", lat: -23.54, lng: -46.62 },
];

const CATEGORIES = ["Criminal", "Família", "Trabalhista", "Consumidor", "Cível"];

const ClientDashboard = () => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showSOSModal, setShowSOSModal] = useState(false);
  const [selectedLawyer, setSelectedLawyer] = useState<typeof MOCK_LAWYERS[0] | null>(null);

  const filteredLawyers = selectedCategory
    ? MOCK_LAWYERS.filter((l) => l.expertise === selectedCategory)
    : MOCK_LAWYERS;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card p-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2">
          <Scale className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold">
            <span className="text-primary">Jus</span>
            <span className="text-accent">Call</span>
          </h1>
        </div>
        <Button variant="ghost" size="icon">
          <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
            JD
          </div>
        </Button>
      </header>

      {/* Category Filter */}
      <div className="border-b border-border bg-card p-4 overflow-x-auto">
        <div className="flex gap-2 min-w-max">
          {CATEGORIES.map((cat) => (
            <Button
              key={cat}
              variant={selectedCategory === cat ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
            >
              {cat}
            </Button>
          ))}
        </div>
      </div>

      {/* Map Area (Placeholder) */}
      <div className="relative flex-1 bg-muted/30">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center space-y-4">
            <MapPin className="h-16 w-16 text-muted-foreground mx-auto" />
            <p className="text-muted-foreground">
              {filteredLawyers.length} advogados disponíveis próximos a você
            </p>
          </div>
        </div>

        {/* Mock Map Pins - Lawyers List */}
        <div className="absolute bottom-4 left-4 right-4 space-y-2 max-h-60 overflow-y-auto">
          {filteredLawyers.map((lawyer) => (
            <Card
              key={lawyer.id}
              className="p-4 cursor-pointer hover:shadow-trust transition-shadow"
              onClick={() => setSelectedLawyer(lawyer)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold">{lawyer.name}</h3>
                  <p className="text-sm text-muted-foreground">{lawyer.oab}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <MapPin className="h-3 w-3 text-accent" />
                    <span className="text-sm text-accent">{lawyer.distance}</span>
                    <Badge variant="secondary" className="text-xs">{lawyer.expertise}</Badge>
                  </div>
                </div>
                <Button size="sm">Ver Perfil</Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* SOS Button */}
      <div className="p-4 bg-card border-t border-border">
        <Button
          variant="emergency"
          size="xl"
          className="w-full"
          onClick={() => setShowSOSModal(true)}
        >
          <AlertCircle className="h-6 w-6" />
          SOS URGÊNCIA / FLAGRANTE
        </Button>
      </div>

      {/* SOS Modal */}
      <Dialog open={showSOSModal} onOpenChange={setShowSOSModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-emergency" />
              Qual o tipo de urgência?
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <Link to="/connection">
              <Button variant="outline" className="w-full justify-start text-left h-auto p-4">
                <div>
                  <p className="font-semibold">Delegacia / Prisão em Flagrante</p>
                  <p className="text-xs text-muted-foreground">Atendimento imediato criminal</p>
                </div>
              </Button>
            </Link>
            <Link to="/connection">
              <Button variant="outline" className="w-full justify-start text-left h-auto p-4">
                <div>
                  <p className="font-semibold">Violência Doméstica</p>
                  <p className="text-xs text-muted-foreground">Proteção e medidas protetivas</p>
                </div>
              </Button>
            </Link>
            <Link to="/connection">
              <Button variant="outline" className="w-full justify-start text-left h-auto p-4">
                <div>
                  <p className="font-semibold">Busca e Apreensão</p>
                  <p className="text-xs text-muted-foreground">Ação judicial em andamento</p>
                </div>
              </Button>
            </Link>
          </div>
        </DialogContent>
      </Dialog>

      {/* Lawyer Details Modal */}
      <Dialog open={!!selectedLawyer} onOpenChange={() => setSelectedLawyer(null)}>
        <DialogContent>
          {selectedLawyer && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedLawyer.name}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="flex items-center justify-center">
                  <div className="h-24 w-24 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold">
                    {selectedLawyer.name.split(" ").map(n => n[0]).join("")}
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm">
                    <span className="font-semibold">OAB:</span> {selectedLawyer.oab}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Distância:</span> {selectedLawyer.distance}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Área:</span> {selectedLawyer.expertise}
                  </p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg text-xs text-muted-foreground">
                  <p className="font-semibold mb-1">Nota de Compliance:</p>
                  <p>De acordo com as normas da OAB, não exibimos avaliações ou classificações de advogados.</p>
                </div>
                <Link to="/connection">
                  <Button className="w-full" size="lg">
                    <Phone className="h-4 w-4" />
                    Solicitar Atendimento
                  </Button>
                </Link>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ClientDashboard;
