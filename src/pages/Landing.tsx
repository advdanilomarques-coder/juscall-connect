import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { MapPin, Shield, Clock, MessageSquare, Scale } from "lucide-react";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-legal-app.jpg";

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold">
              <span className="text-primary">Jus</span>
              <span className="text-accent">Call</span>
            </h1>
          </div>
          <Link to="/auth">
            <Button variant="ghost" size="sm">Entrar</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5" />
        <div className="container mx-auto px-4 py-16 md:py-24 relative">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6 animate-slide-up">
              <h2 className="text-4xl md:text-5xl font-bold text-balance leading-tight">
                Seu advogado, a um toque de distância.
              </h2>
              <p className="text-lg text-muted-foreground text-balance">
                Atendimento jurídico imediato para flagrantes e urgências. Conexão direta, segura e dentro das normas da OAB.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/auth?role=client">
                  <Button size="lg" className="w-full sm:w-auto">
                    Preciso de um Advogado Agora
                  </Button>
                </Link>
                <Link to="/auth?role=lawyer">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    Sou Advogado: Cadastre-se
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <img 
                src={heroImage} 
                alt="JusCall - Conectando você com advogados" 
                className="rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">
            Atendimento Jurídico Quando Você Mais Precisa
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-6 space-y-4 hover:shadow-trust transition-shadow">
              <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <MapPin className="h-6 w-6 text-primary" />
              </div>
              <h4 className="text-xl font-semibold">Geolocalização</h4>
              <p className="text-muted-foreground">
                Encontre advogados próximos a você em tempo real. Atendimento rápido quando minutos importam.
              </p>
            </Card>

            <Card className="p-6 space-y-4 hover:shadow-trust transition-shadow">
              <div className="h-12 w-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                <Clock className="h-6 w-6 text-secondary" />
              </div>
              <h4 className="text-xl font-semibold">Plantão 24h</h4>
              <p className="text-muted-foreground">
                Advogados disponíveis a qualquer hora, incluindo finais de semana e feriados.
              </p>
            </Card>

            <Card className="p-6 space-y-4 hover:shadow-trust transition-shadow">
              <div className="h-12 w-12 rounded-xl bg-accent/10 flex items-center justify-center">
                <Shield className="h-6 w-6 text-accent" />
              </div>
              <h4 className="text-xl font-semibold">Seguro e Regulamentado</h4>
              <p className="text-muted-foreground">
                Todos os advogados são validados pela OAB. Conexão criptografada e segura.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 JusCall. Todos os direitos reservados.</p>
          <Link to="/terms" className="hover:text-primary transition-colors">
            Termos de Uso
          </Link>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
